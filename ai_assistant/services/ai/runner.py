"""
Agent runner that wraps ADK Runner and applies event processing.

This layer sits between AIService and ADK, responsible for:
    1. Running the ADK runner
    2. Processing raw ADK events through agent-specific processors
    3. Yielding processed Content objects
"""

import logging
import uuid
from collections.abc import AsyncGenerator

from google.adk.agents.run_config import StreamingMode
from google.adk.runners import RunConfig
from google.adk.runners import Runner
from google.genai.types import Content as ADKContent
from google.genai.types import Part

from ai_assistant.common.settings import settings
from ai_assistant.domain import Content
from ai_assistant.services.ai.adk.agents.orchestrator.agent import orchestrator_agent
from ai_assistant.services.ai.adk.session_factory import ADKSessionService
from ai_assistant.services.ai.processors.registry import AgentProcessorRegistry

logger = logging.getLogger(__name__)


class AgentRunner:
    """
    Orchestrates agent execution with event processing.

    This class wraps the ADK Runner and applies composable event processors
    to transform raw ADK events into structured Content objects for clients.

    Example:
        runner = AgentRunner(session_service)
        async for content in runner.run_stream(session_id, message, user_id):
            # content could be:
            # - Content(type='loader', data={'message': 'Checking weather...'})
            # - Content(type='message', data={'text': 'The weather is...'})
            # - Content(type='metadata', data={})
    """

    def __init__(
        self,
        session_service: ADKSessionService,
        processor_registry: AgentProcessorRegistry | None = None,
    ) -> None:
        """
        Initialize the agent runner.

        Args:
            session_service: ADK session service for conversation persistence
            processor_registry: Registry of processor pipelines (optional, uses default if None)
        """
        self.session_service = session_service
        self.processor_registry = processor_registry or AgentProcessorRegistry()
        self._adk_runner: Runner | None = None

    def _get_adk_runner(self) -> Runner:
        """
        Get or create the ADK Runner instance.

        Returns:
            Runner: Configured ADK Runner
        """
        if self._adk_runner is None:
            logger.debug('Initializing ADK Runner with orchestrator agent...')
            self._adk_runner = Runner(
                agent=orchestrator_agent,
                app_name=settings.APP_NAME,
                session_service=self.session_service,
            )
            logger.info(f'Initialized ADK Runner for app={settings.APP_NAME}')

        return self._adk_runner

    async def run_stream(
        self,
        session_id: uuid.UUID,
        user_message: str,
        user_id: uuid.UUID,
    ) -> AsyncGenerator[Content, None]:
        """
        Run agent with streaming and event processing.

        This method:
        1. Runs the ADK runner in streaming mode
        2. For each ADK event, determines which agent emitted it
        3. Routes the event to the appropriate processor
        4. Yields Content objects produced by the processor

        Args:
            session_id: Conversation session ID
            user_message: User's input message
            user_id: User ID

        Yields:
            Content: Processed content objects (loaders, messages, metadata, etc.)
        """
        logger.debug(f'Starting agent stream for session {session_id}')

        adk_runner = self._get_adk_runner()
        adk_message = ADKContent(role='user', parts=[Part(text=user_message)])
        message_id = uuid.uuid4()

        async for event in adk_runner.run_async(
            session_id=str(session_id),
            new_message=adk_message,
            user_id=str(user_id),
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        ):
            agent_name = getattr(event, 'author', 'unknown')
            if agent_name == 'user':
                continue

            logger.info(f'Processing event: type={type(event).__name__}, author={agent_name}')

            processors = self.processor_registry.get_processors(agent_name)
            for processor in processors:
                for content in processor.process_event(event, session_id, message_id):
                    logger.info(
                        f'Yielding content: type={content.type}, '
                        f'data_keys={list(content.data.keys())}'
                    )
                    yield content

        logger.debug(f'Agent stream completed for session {session_id}')

    async def run(
        self,
        session_id: uuid.UUID,
        user_message: str,
        user_id: uuid.UUID,
    ) -> str:
        """
        Run agent without streaming (for non-streaming endpoint).

        This collects the complete response and returns just the text.

        Args:
            session_id (uuid.UUID): Conversation session ID
            user_message (str): User's input message
            user_id (uuid.UUID): User ID

        Returns:
            str: Complete response text

        Raises:
            RuntimeError: If no final response received from agent
        """
        logger.debug(f'Starting non-streaming agent run for session {session_id}')

        adk_runner = self._get_adk_runner()

        final_message = None
        async for event in adk_runner.run_async(
            session_id=str(session_id),
            new_message=ADKContent(role='user', parts=[Part(text=user_message)]),
            user_id=str(user_id),
        ):
            if event.is_final_response():
                text_content = ''
                if event.content and event.content.parts:
                    text_content = event.content.parts[0].text or ''
                final_message = text_content

        if final_message is None:
            raise RuntimeError('No final response from agent')

        logger.debug(f'Agent run completed for session {session_id}')
        return final_message
