import logging
from uuid import UUID
from uuid import uuid4

from google.adk.runners import Runner
from google.genai.types import Content
from google.genai.types import Part

from ai_assistant.common.settings import settings
from ai_assistant.domain import Message
from ai_assistant.services.ai.adk.agents.weather_assistant import root_agent
from ai_assistant.services.ai.adk.session_factory import ADKSessionService

logger = logging.getLogger(__name__)


class AIService:
    """
    Service layer for AI interactions.

    Provides a stable interface for the API layer and handles cross-cutting
    concerns like logging, validation, metrics, etc.
    """

    def __init__(self, session_service: ADKSessionService) -> None:
        self.session_service = session_service
        self._runner: Runner | None = None

    def _get_runner(self) -> Runner:
        """
        Get or create the ADK Runner.

        The runner uses the weather agent.

        Returns:
            Runner: ADK Runner instance
        """
        if self._runner is None:
            self._runner = Runner(
                agent=root_agent,
                app_name=settings.APP_NAME,
                session_service=self.session_service,
            )

            logger.info('Created ADK Runner with weather agent')

        return self._runner

    async def run(
        self,
        session_id: UUID,
        user_message: str,
        user_id: str,
    ) -> list[Message]:
        """
        Generate AI response for the given user message.

        Args:
            session_id: The ID of the conversation session
            user_message: The user's message
            user_id: The ID of the user making the request

        Returns:
            List of messages including user message and AI response(s)
        """
        logger.info(f'Processing message for session {session_id}, user {user_id}')

        runner = self._get_runner()

        # Create ADK message object
        message = Content(role='user', parts=[Part(text=user_message)])

        # Run agent - run_async returns an async generator, consume it to get final response
        adk_response = None
        async for response in runner.run_async(
            session_id=str(session_id),
            new_message=message,
            user_id=user_id,
        ):
            adk_response = response  # Get the final response

        if adk_response is None:
            raise RuntimeError('No response from agent')

        # Process response - extract text from Event
        messages = self._process_response(adk_response)

        logger.info(f'Generated {len(messages)} messages for session {session_id}')
        return messages

    def _process_response(self, adk_response) -> list[Message]:
        """
        Process ADK Event response and convert to domain Messages.

        Args:
            adk_response: Event object from ADK Runner

        Returns:
            list[Message]: Domain message objects
        """
        messages = []

        # Only process final responses
        if not adk_response.is_final_response():
            return messages

        # Extract text from Event content
        if hasattr(adk_response, 'content') and adk_response.content:
            content = adk_response.content

            # Extract text from Content object's parts
            content_text = ''
            if hasattr(content, 'parts') and content.parts:
                # Get text from the first part with text
                for part in content.parts:
                    if hasattr(part, 'text') and part.text:
                        content_text = part.text
                        break

            # Determine role from content
            role = content.role if hasattr(content, 'role') else 'assistant'
            # Map 'model' role to 'assistant' for API compatibility
            if role == 'model':
                role = 'assistant'

            messages.append(
                Message(
                    id=uuid4(),
                    content=content_text,
                    role=role,
                    metadata={'agent': 'weather_assistant'},
                )
            )

        return messages
