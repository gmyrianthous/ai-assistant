import logging
from collections.abc import AsyncGenerator
from uuid import UUID
from uuid import uuid4

from google.adk.agents.run_config import StreamingMode
from google.adk.runners import RunConfig
from google.adk.runners import Runner
from google.genai.types import Content
from google.genai.types import Part
from langfuse import observe

from ai_assistant.common.clients.langfuse import get_langfuse_client
from ai_assistant.common.settings import settings
from ai_assistant.domain import Message
from ai_assistant.domain import StreamChunk
from ai_assistant.services.ai.adk.agents.weather_assistant import root_agent
from ai_assistant.services.ai.adk.session_factory import ADKSessionService

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, session_service: ADKSessionService) -> None:
        self.session_service = session_service
        self._runner: Runner | None = None

    def _get_runner(self) -> Runner:
        """
        Get or create the ADK Runner.

        Returns:
            Runner: ADK Runner instance
        """
        if self._runner is None:
            self._runner = Runner(
                agent=root_agent,
                app_name=settings.APP_NAME,
                session_service=self.session_service,
            )
            logger.info(f'Initialised ADK Runner for app={settings.APP_NAME}')

        return self._runner

    @observe
    async def run(
        self,
        session_id: UUID,
        user_message: str,
        user_id: UUID,
    ) -> Message:
        """
        Generate AI response for the given user message.

        Args:
            session_id: The ID of the conversation session
            user_message: The user's message
            user_id: The ID of the user making the request

        Returns:
            List of messages including user message and AI response(s)
        """
        logger.debug(f'Processing message for session {session_id}, user {user_id}')

        runner = self._get_runner()
        message = Content(role='user', parts=[Part(text=user_message)])

        async for event in runner.run_async(
            session_id=str(session_id),
            new_message=message,
            user_id=str(user_id),
        ):
            if event.is_final_response():
                text_content = ''
                if event.content and event.content.parts:
                    text_content = event.content.parts[0].text or ''

                final_message = Message(
                    id=uuid4(),
                    content=text_content,
                    role='assistant',
                    metadata={'session_id': session_id},
                )
                # Do not break, since OpenTelemetry wraps the async generator with tracing context
                # By fully consuming the generator (not breaking), OpenTelemetry can properly
                # detach contexts

        if not final_message:
            raise RuntimeError('No final response from agent')

        langfuse = get_langfuse_client()
        langfuse.update_current_trace(
            user_id=str(user_id),
            session_id=str(session_id),
            input=user_message,
            output=final_message.content,
        )

        logger.debug(f'Generated message for session {session_id}')
        return final_message

    @observe
    async def run_stream(
        self,
        session_id: UUID,
        user_message: str,
        user_id: UUID,
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Generate streaming AI response for the given user message.

        Args:
            session_id: The ID of the conversation session
            user_message: The user's message
            user_id: The ID of the user making the request

        Yields:
            StreamChunk: Content chunks with metadata
        """
        logger.debug(f'Processing streaming message for session {session_id}, user {user_id}')

        runner = self._get_runner()
        message = Content(role='user', parts=[Part(text=user_message)])

        message_id = uuid4()
        full_output_message = ''
        async for event in runner.run_async(
            session_id=str(session_id),
            new_message=message,
            user_id=str(user_id),
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        ):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            full_output_message += part.text
                            yield StreamChunk(
                                id=message_id,
                                role='assistant',
                                content=part.text,
                            )

        # Final chunk with metadata
        yield StreamChunk(
            id=message_id,
            role='assistant',
            content='',
            metadata={
                'session_id': str(session_id),
            },
        )

        logger.debug(f'Stream completed for session {session_id}')

        langfuse = get_langfuse_client()
        langfuse.update_current_trace(
            user_id=str(user_id),
            session_id=str(session_id),
            input=user_message,
            output=full_output_message,
        )
