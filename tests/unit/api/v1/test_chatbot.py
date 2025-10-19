from unittest.mock import AsyncMock
from uuid import uuid4

from ai_assistant.api.v1.routes.chatbot import chat
from ai_assistant.api.v1.schemas.chat import ChatRequest
from ai_assistant.api.v1.schemas.chat import ContentResponse
from ai_assistant.domain import Content
from ai_assistant.services.ai.service import AIService


class TestChatEndpoint:
    async def test_chat_success(self) -> None:
        # arrange
        ai_service = AsyncMock(spec=AIService)
        session_id = uuid4()
        user_id = uuid4()
        user_message = 'Hello, AI!'
        request = ChatRequest(
            session_id=session_id,
            message=user_message,
            user_id=user_id,
        )

        domain_content = Content(
            id=uuid4(),
            type='message',
            data={'text': 'Hello, human!'},
            metadata={'session_id': str(session_id)},
        )
        ai_service.run = AsyncMock(return_value=domain_content)

        # act
        result = await chat(request, ai_service)

        # assert
        assert isinstance(result, ContentResponse)
        assert result.type == 'message'
        assert result.data == {'text': 'Hello, human!'}
        assert result.metadata == {'session_id': str(session_id)}

        ai_service.run.assert_called_once_with(
            session_id=session_id,
            user_message=user_message,
            user_id=user_id,
        )

    async def test_chat_with_metadata(self) -> None:
        # arrange
        ai_service = AsyncMock(spec=AIService)
        session_id = uuid4()
        user_id = uuid4()
        user_message = 'Test with metadata'
        request = ChatRequest(
            session_id=session_id,
            message=user_message,
            user_id=user_id,
        )

        domain_content = Content(
            id=uuid4(),
            type='message',
            data={'text': 'Response with metadata'},
            metadata={'provider': 'adk', 'confidence': 0.95},
        )
        ai_service.run = AsyncMock(return_value=domain_content)

        # act
        result = await chat(request, ai_service)

        # assert
        assert result.metadata == {'provider': 'adk', 'confidence': 0.95}

    async def test_content_response_from_domain_model_conversion(self) -> None:
        # arrange
        ai_service = AsyncMock(spec=AIService)
        session_id = uuid4()
        user_id = uuid4()
        content_id = uuid4()
        request = ChatRequest(
            session_id=session_id,
            message='Test conversion',
            user_id=user_id,
        )

        domain_content = Content(
            id=content_id,
            type='message',
            data={'text': 'Test message'},
            metadata={'test': 'value', 'number': 42},
        )
        ai_service.run = AsyncMock(return_value=domain_content)

        # act
        result = await chat(request, ai_service)

        # assert
        assert result.id == content_id
        assert result.type == 'message'
        assert result.data == {'text': 'Test message'}
        assert result.metadata == {'test': 'value', 'number': 42}

    async def test_chat_preserves_content_ids(self) -> None:
        # arrange
        ai_service = AsyncMock(spec=AIService)
        session_id = uuid4()
        user_id = uuid4()
        content_id = uuid4()
        request = ChatRequest(
            session_id=session_id,
            message='Test ID preservation',
            user_id=user_id,
        )

        domain_content = Content(
            id=content_id,
            type='message',
            data={'text': 'Response'},
            metadata=None,
        )
        ai_service.run = AsyncMock(return_value=domain_content)

        # act
        result = await chat(request, ai_service)

        # assert
        assert result.id == content_id
