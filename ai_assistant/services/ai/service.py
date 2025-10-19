import logging
import uuid
from collections.abc import AsyncGenerator

from langfuse import observe

from ai_assistant.common.clients.langfuse import get_langfuse_client
from ai_assistant.domain import Content
from ai_assistant.services.ai.adk.session_factory import ADKSessionService
from ai_assistant.services.ai.runner import AgentRunner

logger = logging.getLogger(__name__)


class AIService:
    def __init__(
        self,
        session_service: ADKSessionService,
        agent_runner: AgentRunner | None = None,
    ) -> None:
        self.session_service = session_service
        self.agent_runner = agent_runner or AgentRunner(session_service)

    @observe
    async def run(
        self,
        session_id: uuid.UUID,
        user_message: str,
        user_id: uuid.UUID,
    ) -> Content:
        """
        Generate AI response (non-streaming).

        Args:
            session_id: Conversation session ID
            user_message: User's message
            user_id: User ID

        Returns:
            Content: Response as Content(type='message', ...)
        """
        logger.debug(f'Processing message for session {session_id}, user {user_id}')
        response_text = await self.agent_runner.run(
            session_id=session_id,
            user_message=user_message,
            user_id=user_id,
        )

        langfuse = get_langfuse_client()
        langfuse.update_current_trace(
            user_id=str(user_id),
            session_id=str(session_id),
            input=user_message,
            output=response_text,
        )

        return Content(
            id=uuid.uuid4(),
            type='message',
            data={'text': response_text},
            metadata={'session_id': str(session_id)},
        )

    @observe
    async def run_stream(
        self,
        session_id: uuid.UUID,
        user_message: str,
        user_id: uuid.UUID,
    ) -> AsyncGenerator[Content, None]:
        """
        Generate streaming AI response.

        Args:
            session_id(uuid.UUID): Conversation session ID
            user_message(str): User's message
            user_id(uuid.UUID): User ID

        Yields:
            AsyncGenerator[Content, None]: Processed content objects
        """
        logger.debug(f'Processing streaming message for session {session_id}, user {user_id}')

        full_output = ''
        async for content in self.agent_runner.run_stream(
            session_id=session_id,
            user_message=user_message,
            user_id=user_id,
        ):
            if content.type == 'message' and 'text' in content.data:
                full_output += content.data['text']
            yield content

        langfuse = get_langfuse_client()
        langfuse.update_current_trace(
            user_id=str(user_id),
            session_id=str(session_id),
            input=user_message,
            output=full_output,
        )

        logger.debug(f'Stream completed for session {session_id}')
