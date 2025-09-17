from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock
from unittest.mock import Mock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistant.domain import Message
from ai_assistant.services.ai.providers.base import AIProvider
from ai_assistant.services.ai.service import AIService


class TestAIService:
    async def test_ai_service_initialisation(
        self,
        ai_service: AIService,
        ai_provider: AIProvider,
        db_session: AsyncSession,
    ) -> None:
        # arrange
        expected_messages = [
            Message(id=uuid4(), content='Test message with real DB', role='user'),
            Message(id=uuid4(), content='This is supposed to be a AI response!', role='assistant'),
        ]
        ai_provider.generate_response.return_value = expected_messages
        session_id = uuid4()
        user_message = 'Test message with real DB'

        # act
        result = await ai_service.generate_response(session_id, user_message)

        # assert
        assert ai_service.db_session is db_session
        assert ai_service.provider is not None
        assert result == expected_messages

    async def test_generate_response(
        self,
        ai_service: AIService,
        ai_provider: AIProvider,
        db_session: AsyncSession,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_message = 'Hello, world!'
        expected_messages = [
            Message(id=uuid4(), content=user_message, role='user'),
            Message(id=uuid4(), content=f'Response for session {session_id}', role='assistant'),
        ]
        ai_provider.generate_response.return_value = expected_messages

        # act
        result = await ai_service.generate_response(session_id, user_message)

        # assert
        assert result == expected_messages
        ai_provider.generate_response.assert_called_once_with(session_id, user_message)

    async def test_generate_stream_response(
        self,
        ai_service: AIService,
        ai_provider: AIProvider,
        db_session: AsyncSession,
    ) -> None:
        # arrange
        async def mock_stream() -> AsyncGenerator[str, None]:
            yield 'This,'
            yield ' is supposed to be a AI'
            yield ' response!'

        ai_provider.generate_stream_response.return_value = mock_stream()
        session_id = uuid4()
        user_message = 'Hello, world!'

        # act
        result_chunks = []
        async for chunk in ai_service.generate_stream_response(session_id, user_message):
            result_chunks.append(chunk)

        # assert
        assert result_chunks == ['This,', ' is supposed to be a AI', ' response!']
        ai_provider.generate_stream_response.assert_called_once_with(session_id, user_message)

    async def test_multiple_operations_with_same_session(
        self,
        ai_service: AIService,
        ai_provider: AIProvider,
        db_session: AsyncSession,
    ) -> None:
        # arrange
        expected_messages = [
            Message(id=uuid4(), content='Test message', role='user'),
            Message(id=uuid4(), content='This is supposed to be a AI response!', role='assistant'),
        ]
        ai_provider.generate_response.return_value = expected_messages

        async def mock_stream() -> AsyncGenerator[str, None]:
            yield 'This,'
            yield ' is supposed to be a AI'
            yield ' response!'

        ai_provider.generate_stream_response.return_value = mock_stream()
        session_id = uuid4()

        # act
        result1 = await ai_service.generate_response(session_id, 'First message')
        result2 = await ai_service.generate_response(session_id, 'Second message')

        stream_chunks = []
        async for chunk in ai_service.generate_stream_response(session_id, 'Stream message'):
            stream_chunks.append(chunk)

        # assert
        assert result1 == expected_messages
        assert result2 == expected_messages
        assert stream_chunks == ['This,', ' is supposed to be a AI', ' response!']
        assert ai_provider.generate_response.call_count == 2
        assert ai_provider.generate_stream_response.call_count == 1

    async def test_service_isolation_between_sessions(
        self,
        db_session: AsyncSession,
    ) -> None:
        # arrange
        session_id1 = uuid4()
        session_id2 = uuid4()

        messages1 = [
            Message(id=uuid4(), content='Test 1', role='user'),
            Message(id=uuid4(), content='Response from provider 1', role='assistant'),
        ]
        messages2 = [
            Message(id=uuid4(), content='Test 2', role='user'),
            Message(id=uuid4(), content='Response from provider 2', role='assistant'),
        ]

        provider1 = Mock()
        provider1.generate_response = AsyncMock(return_value=messages1)
        provider1.generate_stream_response = Mock()
        provider1.cleanup = AsyncMock()

        provider2 = Mock()
        provider2.generate_response = AsyncMock(return_value=messages2)
        provider2.generate_stream_response = Mock()
        provider2.cleanup = AsyncMock()

        service1 = AIService(db_session=db_session, provider=provider1)
        service2 = AIService(db_session=db_session, provider=provider2)

        # act
        result1 = await service1.generate_response(session_id1, 'Test 1')
        result2 = await service2.generate_response(session_id2, 'Test 2')

        # assert
        assert result1 == messages1
        assert result2 == messages2
        provider1.generate_response.assert_called_once_with(session_id1, 'Test 1')
        provider2.generate_response.assert_called_once_with(session_id2, 'Test 2')
