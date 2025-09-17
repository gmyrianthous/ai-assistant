from collections.abc import AsyncGenerator
from uuid import uuid4

from ai_assistant.domain import Message
from ai_assistant.services.ai.providers.base import AIProvider
from ai_assistant.services.ai.service import AIService


class TestAIService:
    async def test_generate_response_delegates_to_provider(
        self,
        ai_service: AIService,
        ai_provider: AIProvider,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_message = 'Hello, AI!'
        expected_messages = [
            Message(id=uuid4(), content=user_message, role='user'),
            Message(id=uuid4(), content='Hello, human!', role='assistant'),
        ]
        ai_provider.generate_response.return_value = expected_messages

        # act
        result = await ai_service.generate_response(session_id, user_message)

        # assert
        assert result == expected_messages
        ai_provider.generate_response.assert_called_once_with(session_id, user_message)

    async def test_generate_stream_response_delegates_to_provider(
        self,
        ai_service: AIService,
        ai_provider: AIProvider,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_message = 'Hello, AI!'
        expected_chunks = ['Hello', ' human', '!']

        async def mock_stream() -> AsyncGenerator[str, None]:
            for chunk in expected_chunks:
                yield chunk

        ai_provider.generate_stream_response.return_value = mock_stream()

        # act
        result_chunks = []
        async for chunk in ai_service.generate_stream_response(session_id, user_message):
            result_chunks.append(chunk)

        # assert
        assert result_chunks == expected_chunks
        ai_provider.generate_stream_response.assert_called_once_with(session_id, user_message)
