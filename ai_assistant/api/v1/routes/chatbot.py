import logging
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from ai_assistant.api.dependencies import get_ai_service
from ai_assistant.api.v1.schemas.chat import ChatRequest
from ai_assistant.api.v1.schemas.chat import ChatResponse
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
) -> ChatResponse:
    """
    Process an input chat request via AI service and return the response back to the client.

    Args:
        request (ChatRequest): The chat request containing the session ID and message.
        ai_service (AIService): The AI service to use to generate the response.

    Returns:
        ChatResponse: The chat response containing the messages.
    """
    logger.info(f'New chat request received for session {request.session_id}')

    domain_messages = await ai_service.generate_response(
        session_id=request.session_id,
        user_message=request.message,
    )

    response_messages = [MessageSchema.from_domain_model(msg) for msg in domain_messages]

    return ChatResponse(messages=response_messages)
