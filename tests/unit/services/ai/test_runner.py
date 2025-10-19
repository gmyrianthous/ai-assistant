from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest

from ai_assistant.services.ai.processors.registry import AgentProcessorRegistry
from ai_assistant.services.ai.processors.text_content_processor import TextContentProcessor
from ai_assistant.services.ai.processors.tool_call_processor import ToolCallProcessor
from ai_assistant.services.ai.runner import AgentRunner
from tests.factories import ADKEventFactory


async def async_generator(items):
    for item in items:
        yield item


@pytest.fixture
def session_service():
    return MagicMock()


@pytest.fixture
def processor_registry():
    registry = MagicMock(spec=AgentProcessorRegistry)
    registry.get_processors.return_value = [
        TextContentProcessor(),
    ]
    return registry


@pytest.fixture
def runner(session_service, processor_registry):
    return AgentRunner(
        session_service=session_service,
        processor_registry=processor_registry,
    )


class TestInitialization:
    def test_initializes_with_session_service(
        self,
        session_service: MagicMock,
    ) -> None:
        # arrange & act
        runner = AgentRunner(session_service=session_service)

        # assert
        assert runner.session_service is session_service
        assert runner.processor_registry is not None
        assert runner._adk_runner is None

    def test_initializes_with_custom_processor_registry(
        self,
        session_service: MagicMock,
        processor_registry: MagicMock,
    ) -> None:
        # arrange & act
        runner = AgentRunner(
            session_service=session_service,
            processor_registry=processor_registry,
        )

        # assert
        assert runner.processor_registry is processor_registry

    def test_creates_default_registry_if_none_provided(self, session_service) -> None:
        # arrange & act
        runner = AgentRunner(session_service=session_service)

        # assert
        assert isinstance(runner.processor_registry, AgentProcessorRegistry)


class TestRunStream:
    @pytest.mark.asyncio
    async def test_yields_content_from_processors(
        self,
        runner: AgentRunner,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        mock_events = [
            ADKEventFactory.with_text('Hello', author='test_agent'),
            ADKEventFactory.with_text(' world', author='test_agent'),
        ]

        mock_adk_runner = MagicMock()
        mock_adk_runner.run_async = MagicMock(return_value=async_generator(mock_events))

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            contents = []
            async for content in runner.run_stream(
                session_id=session_id,
                user_message='Test message',
                user_id=user_id,
            ):
                contents.append(content)

        # assert
        assert len(contents) == 2
        assert contents[0].type == 'message'
        assert contents[0].data['text'] == 'Hello'
        assert contents[1].data['text'] == ' world'

    @pytest.mark.asyncio
    async def test_skips_user_events(
        self,
        runner: AgentRunner,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        mock_events = [
            ADKEventFactory.with_text('User input', author='user'),
            ADKEventFactory.with_text('Agent response', author='test_agent'),
        ]

        mock_adk_runner = MagicMock()
        mock_adk_runner.run_async = MagicMock(return_value=async_generator(mock_events))

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            contents = []
            async for content in runner.run_stream(
                session_id=session_id,
                user_message='Test',
                user_id=user_id,
            ):
                contents.append(content)

        # assert
        assert len(contents) == 1
        assert contents[0].data['text'] == 'Agent response'

    @pytest.mark.asyncio
    async def test_extracts_agent_name_from_author(
        self,
        runner: AgentRunner,
        processor_registry: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        mock_event = ADKEventFactory.with_text('Hello', author='weather_assistant')

        mock_adk_runner = MagicMock()
        mock_adk_runner.run_async = MagicMock(return_value=async_generator([mock_event]))

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            async for _ in runner.run_stream(
                session_id=session_id,
                user_message='Test',
                user_id=user_id,
            ):
                pass

        # assert
        processor_registry.get_processors.assert_called_with('weather_assistant')

    @pytest.mark.asyncio
    async def test_uses_unknown_for_missing_author(
        self,
        runner: AgentRunner,
        processor_registry: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        mock_event = MagicMock()
        mock_event.author = 'unknown'
        mock_event.content = None

        mock_adk_runner = MagicMock()
        mock_adk_runner.run_async = MagicMock(return_value=async_generator([mock_event]))

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            async for _ in runner.run_stream(
                session_id=session_id,
                user_message='Test',
                user_id=user_id,
            ):
                pass

        # assert
        processor_registry.get_processors.assert_called_with('unknown')

    @pytest.mark.asyncio
    async def test_executes_all_processors_for_agent(
        self,
        session_service: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        tool_processor = MagicMock(spec=ToolCallProcessor)
        tool_processor.process_event.return_value = iter([])

        text_processor = MagicMock(spec=TextContentProcessor)
        text_processor.process_event.return_value = iter([])

        registry = MagicMock(spec=AgentProcessorRegistry)
        registry.get_processors.return_value = [tool_processor, text_processor]

        runner_with_custom_registry = AgentRunner(
            session_service=session_service,
            processor_registry=registry,
        )

        mock_event = ADKEventFactory.with_text('Hello', author='test_agent')

        mock_adk_runner = MagicMock()
        mock_adk_runner.run_async = MagicMock(return_value=async_generator([mock_event]))

        with patch.object(
            runner_with_custom_registry, '_get_adk_runner', return_value=mock_adk_runner
        ):
            # act
            async for _ in runner_with_custom_registry.run_stream(
                session_id=session_id,
                user_message='Test',
                user_id=user_id,
            ):
                pass

        # assert
        tool_processor.process_event.assert_called_once()
        text_processor.process_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_passes_correct_context_to_processors(
        self,
        session_service: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        processor = MagicMock()
        processor.process_event.return_value = iter([])

        registry = MagicMock(spec=AgentProcessorRegistry)
        registry.get_processors.return_value = [processor]

        runner_with_custom_registry = AgentRunner(
            session_service=session_service,
            processor_registry=registry,
        )

        mock_event = ADKEventFactory.with_text('Hello', author='test_agent')

        mock_adk_runner = MagicMock()
        mock_adk_runner.run_async = MagicMock(return_value=async_generator([mock_event]))

        with patch.object(
            runner_with_custom_registry, '_get_adk_runner', return_value=mock_adk_runner
        ):
            # act
            async for _ in runner_with_custom_registry.run_stream(
                session_id=session_id,
                user_message='Test',
                user_id=user_id,
            ):
                pass

        # assert
        call_args = processor.process_event.call_args
        assert call_args[0][0] == mock_event
        assert call_args[0][1] == session_id


class TestRun:
    @pytest.mark.asyncio
    async def test_returns_final_response_text(
        self,
        runner: AgentRunner,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        mock_event = ADKEventFactory.final_response(
            text='Final response text', author='test_agent'
        )

        mock_adk_runner = MagicMock()
        mock_adk_runner.run_async = MagicMock(return_value=async_generator([mock_event]))

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            result = await runner.run(
                session_id=session_id,
                user_message='Test',
                user_id=user_id,
            )

        # assert
        assert result == 'Final response text'

    @pytest.mark.asyncio
    async def test_raises_error_when_no_final_response(
        self,
        runner: AgentRunner,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        mock_event = ADKEventFactory.with_text('Not final', author='test_agent', is_final=False)

        mock_adk_runner = MagicMock()
        mock_adk_runner.run_async = MagicMock(return_value=async_generator([mock_event]))

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act & assert
            with pytest.raises(RuntimeError, match='No final response from agent'):
                await runner.run(
                    session_id=session_id,
                    user_message='Test',
                    user_id=user_id,
                )

    @pytest.mark.asyncio
    async def test_handles_empty_response_text(
        self,
        runner: AgentRunner,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        mock_event = ADKEventFactory.final_response(text='', author='test_agent')

        mock_adk_runner = MagicMock()
        mock_adk_runner.run_async = MagicMock(return_value=async_generator([mock_event]))

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            result = await runner.run(
                session_id=session_id,
                user_message='Test',
                user_id=user_id,
            )

        # assert
        assert result == ''


class TestGetAdkRunner:
    def test_creates_runner_on_first_call(
        self,
        runner: AgentRunner,
    ) -> None:
        # arrange
        with patch('ai_assistant.services.ai.runner.Runner') as mock_runner_class:
            mock_runner_instance = MagicMock()
            mock_runner_class.return_value = mock_runner_instance

            # act
            result = runner._get_adk_runner()

        # assert
        assert result is mock_runner_instance
        mock_runner_class.assert_called_once()

    def test_returns_cached_runner_on_subsequent_calls(
        self,
        runner: AgentRunner,
    ) -> None:
        # arrange
        with patch('ai_assistant.services.ai.runner.Runner') as mock_runner_class:
            mock_runner_instance = MagicMock()
            mock_runner_class.return_value = mock_runner_instance

            # act
            first_call = runner._get_adk_runner()
            second_call = runner._get_adk_runner()

        # assert
        assert first_call is second_call
        mock_runner_class.assert_called_once()
