from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest

from ai_assistant.domain import Content
from ai_assistant.services.ai.service import AIService


async def async_generator(items: list[Content]) -> AsyncGenerator[Content, None]:
    """Helper to create async generator from list of items."""
    for item in items:
        yield item


@pytest.fixture
def session_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def agent_runner() -> MagicMock:
    runner = MagicMock()
    runner.run = AsyncMock()
    runner.run_stream = MagicMock()
    return runner


@pytest.fixture
def ai_service(session_service: MagicMock, agent_runner: MagicMock) -> AIService:
    return AIService(
        session_service=session_service,
        agent_runner=agent_runner,
    )


class TestInitialization:
    def test_initializes_with_dependencies(
        self,
        session_service: MagicMock,
        agent_runner: MagicMock,
    ) -> None:
        # arrange & act
        service = AIService(
            session_service=session_service,
            agent_runner=agent_runner,
        )

        # assert
        assert service.session_service is session_service
        assert service.agent_runner is agent_runner


class TestRun:
    @pytest.mark.asyncio
    @patch('ai_assistant.services.ai.service.get_langfuse_client')
    async def test_returns_content_with_message_type(
        self,
        mock_langfuse_client: MagicMock,
        ai_service: AIService,
        agent_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        user_message = 'Test message'

        agent_runner.run.return_value = 'Agent response text'

        # act
        result = await ai_service.run(
            session_id=session_id,
            user_message=user_message,
            user_id=user_id,
        )

        # assert
        assert isinstance(result, Content)
        assert result.type == 'message'
        assert result.data is not None
        assert result.data['text'] == 'Agent response text'
        assert result.metadata is not None
        assert result.metadata['session_id'] == str(session_id)

    @pytest.mark.asyncio
    @patch('ai_assistant.services.ai.service.get_langfuse_client')
    async def test_calls_agent_runner_with_correct_params(
        self,
        mock_langfuse_client: MagicMock,
        ai_service: AIService,
        agent_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        user_message = 'Test message'

        agent_runner.run.return_value = 'Agent response'

        # act
        await ai_service.run(
            session_id=session_id,
            user_message=user_message,
            user_id=user_id,
        )

        # assert
        agent_runner.run.assert_called_once_with(
            session_id=session_id,
            user_message=user_message,
            user_id=user_id,
        )

    @pytest.mark.asyncio
    @patch('ai_assistant.services.ai.service.get_langfuse_client')
    async def test_updates_langfuse_trace(
        self,
        mock_langfuse_client: MagicMock,
        ai_service: AIService,
        agent_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        user_message = 'Test message'

        agent_runner.run.return_value = 'Agent response'

        # act
        await ai_service.run(
            session_id=session_id,
            user_message=user_message,
            user_id=user_id,
        )

        # assert
        mock_langfuse_client.return_value.update_current_trace.assert_called_once_with(
            user_id=str(user_id),
            session_id=str(session_id),
            input=user_message,
            output='Agent response',
        )

    @pytest.mark.asyncio
    @patch('ai_assistant.services.ai.service.get_langfuse_client')
    async def test_generates_unique_message_id(
        self,
        mock_langfuse_client: MagicMock,
        ai_service: AIService,
        agent_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        agent_runner.run.return_value = 'Response 1'

        # act
        result1 = await ai_service.run(
            session_id=session_id,
            user_message='Message 1',
            user_id=user_id,
        )

        agent_runner.run.return_value = 'Response 2'

        result2 = await ai_service.run(
            session_id=session_id,
            user_message='Message 2',
            user_id=user_id,
        )

        # assert
        assert result1.id != result2.id


class TestRunStream:
    @pytest.mark.asyncio
    @patch('ai_assistant.services.ai.service.get_langfuse_client')
    async def test_yields_content_from_agent_runner(
        self,
        mock_langfuse_client: MagicMock,
        ai_service: AIService,
        agent_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        user_message = 'Test message'

        mock_contents = [
            Content(
                id=uuid4(),
                type='loader',
                data={'message': 'Loading...'},
                metadata={},
            ),
            Content(
                id=uuid4(),
                type='message',
                data={'text': 'Response text'},
                metadata={},
            ),
        ]

        agent_runner.run_stream.return_value = async_generator(mock_contents)

        # act
        results = []
        async for content in ai_service.run_stream(
            session_id=session_id,
            user_message=user_message,
            user_id=user_id,
        ):
            results.append(content)

        # assert
        assert len(results) == 2
        assert results[0].type == 'loader'
        assert results[0].data['message'] == 'Loading...'
        assert results[1].type == 'message'
        assert results[1].data['text'] == 'Response text'

    @pytest.mark.asyncio
    @patch('ai_assistant.services.ai.service.get_langfuse_client')
    async def test_calls_agent_runner_stream_with_correct_params(
        self,
        mock_langfuse_client: MagicMock,
        ai_service: AIService,
        agent_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        user_message = 'Test message'

        agent_runner.run_stream.return_value = async_generator([])

        # act
        async for _ in ai_service.run_stream(
            session_id=session_id,
            user_message=user_message,
            user_id=user_id,
        ):
            pass

        # assert
        agent_runner.run_stream.assert_called_once_with(
            session_id=session_id,
            user_message=user_message,
            user_id=user_id,
        )

    @pytest.mark.asyncio
    @patch('ai_assistant.services.ai.service.get_langfuse_client')
    async def test_updates_langfuse_trace_for_streaming(
        self,
        mock_langfuse_client: MagicMock,
        ai_service: AIService,
        agent_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        user_message = 'Test message'

        mock_content = Content(
            id=uuid4(),
            type='message',
            data={'text': 'Response'},
            metadata={},
        )

        agent_runner.run_stream.return_value = async_generator([mock_content])

        # act
        async for _ in ai_service.run_stream(
            session_id=session_id,
            user_message=user_message,
            user_id=user_id,
        ):
            pass

        # assert
        mock_langfuse_client.return_value.update_current_trace.assert_called_once_with(
            user_id=str(user_id),
            session_id=str(session_id),
            input=user_message,
            output='Response',
        )

    @pytest.mark.asyncio
    @patch('ai_assistant.services.ai.service.get_langfuse_client')
    async def test_passes_through_all_content_types(
        self,
        mock_langfuse_client: MagicMock,
        ai_service: AIService,
        agent_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        mock_contents = [
            Content(
                id=uuid4(),
                type='loader',
                data={'message': 'Thinking...', 'show_spinner': True},
                metadata={},
            ),
            Content(
                id=uuid4(),
                type='message',
                data={'text': 'Partial '},
                metadata={},
            ),
            Content(
                id=uuid4(),
                type='message',
                data={'text': 'text'},
                metadata={},
            ),
            Content(
                id=uuid4(),
                type='metadata',
                data={'tokens_used': 100},
                metadata={},
            ),
        ]

        agent_runner.run_stream.return_value = async_generator(mock_contents)

        # act
        results = []
        async for content in ai_service.run_stream(
            session_id=session_id,
            user_message='Test',
            user_id=user_id,
        ):
            results.append(content)

        # assert
        assert len(results) == 4
        assert [r.type for r in results] == ['loader', 'message', 'message', 'metadata']

    @pytest.mark.asyncio
    @patch('ai_assistant.services.ai.service.get_langfuse_client')
    async def test_handles_empty_stream(
        self,
        mock_langfuse_client: MagicMock,
        ai_service: AIService,
        agent_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()

        agent_runner.run_stream.return_value = async_generator([])

        # act
        results = []
        async for content in ai_service.run_stream(
            session_id=session_id,
            user_message='Test',
            user_id=user_id,
        ):
            results.append(content)

        # assert
        assert len(results) == 0
