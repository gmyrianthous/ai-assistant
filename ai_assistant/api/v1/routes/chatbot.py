import json
import logging
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi.responses import StreamingResponse

from ai_assistant.api.dependencies import get_ai_service
from ai_assistant.api.v1.schemas.chat import ChatRequest
from ai_assistant.api.v1.schemas.chat import MessageSchema
from ai_assistant.services.ai.service import AIService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    '/chat',
    summary='Chat with the AI assistant and get the full response',
    status_code=status.HTTP_200_OK,
)
async def chat(
    request: ChatRequest,
    ai_service: Annotated[AIService, Depends(get_ai_service)],
) -> MessageSchema:
    """
    Process an input chat request via AI service and return the response back to the client.

    Args:
        request (ChatRequest): The chat request containing the session ID and message.
        ai_service (AIService): The AI service to use to generate the response.

    Returns:
        MessageSchema: The assistant's message response.
    """
    logger.info(f'New chat request received for session {request.session_id}')

    domain_message = await ai_service.run(
        session_id=request.session_id,
        user_message=request.message,
        user_id=request.user_id,
    )

    return MessageSchema.from_domain_model(domain_message)


@router.post(
    '/chat/stream',
    summary='Chat with the AI assistant and stream the response using Server-Sent Events (SSE)',
    status_code=status.HTTP_200_OK,
)
async def chat_stream(
    request: ChatRequest,
    ai_service: Annotated[AIService, Depends(get_ai_service)],
) -> StreamingResponse:
    """
    Process a chat request and stream the AI response using Server-Sent Events.

    The response is streamed as SSE events in the format:
    ```
    data: {"content": "chunk", "done": false}

    data: {"content": "", "done": true, "metadata": {"session_id": "..."}}
    ```

    Args:
        request: The chat request containing the session ID and message
        ai_service: The AI service to use to generate the response

    Returns:
        StreamingResponse: SSE stream of response chunks
    """
    logger.info(f'New chat stream request for session {request.session_id}')

    async def event_generator():
        """Generate Server-Sent Events from domain StreamChunks."""
        try:
            async for chunk in ai_service.run_stream(
                session_id=request.session_id,
                user_message=request.message,
                user_id=request.user_id,
            ):
                event_data = MessageSchema(
                    id=chunk.id,
                    role=chunk.role,
                    content=chunk.content,
                    metadata=chunk.metadata,
                )

                # Format as SSE: "data: {json}\n\n"
                yield f'data: {event_data.model_dump_json()}\n\n'

            logger.info(f'Stream completed for session {request.session_id}')

        except Exception as e:
            logger.error(f'Error during streaming for session {request.session_id}: {e}')

            # Send error event
            error_event = {
                'error': str(e),
                'session_id': request.session_id,
            }

            yield f'data: {json.dumps(error_event)}\n\n'

    return StreamingResponse(
        event_generator(),
        media_type='text/event-stream',
    )
