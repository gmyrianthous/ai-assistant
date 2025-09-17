from unittest.mock import AsyncMock
from uuid import uuid4

from ai_assistant.api.v1.routes.chatbot import chat
from ai_assistant.api.v1.schemas.chat import ChatRequest
from ai_assistant.api.v1.schemas.chat import ChatResponse
from ai_assistant.api.v1.schemas.chat import MessageSchema
from ai_assistant.domain import Message
from ai_assistant.services.ai.service import AIService


class TestChatEndpoint:
    async def test_chat_success(self, ai_service: AIService) -> None:
        # arrange
        session_id = uuid4()
        user_message = 'Hello, AI!'
        request = ChatRequest(session_id=session_id, message=user_message)

        domain_messages = [
            Message(id=uuid4(), content=user_message, role='user', metadata=None),
            Message(
                id=uuid4(),
                content='Hello, human!',
                role='assistant',
                metadata={'provider': 'test'},
            ),
        ]
        ai_service.generate_response = AsyncMock(return_value=domain_messages)

        # act
        result = await chat(request, ai_service)

        # assert
        assert isinstance(result, ChatResponse)
        assert len(result.messages) == 2

        user_msg = result.messages[0]
        assert isinstance(user_msg, MessageSchema)
        assert user_msg.content == user_message
        assert user_msg.role == 'user'
        assert user_msg.metadata is None

        assistant_msg = result.messages[1]
        assert isinstance(assistant_msg, MessageSchema)
        assert assistant_msg.content == 'Hello, human!'
        assert assistant_msg.role == 'assistant'
        assert assistant_msg.metadata == {'provider': 'test'}

        ai_service.generate_response.assert_called_once_with(
            session_id=session_id, user_message=user_message
        )

    async def test_chat_with_metadata(self, ai_service: AIService) -> None:
        # arrange
        session_id = uuid4()
        user_message = 'Test with metadata'
        request = ChatRequest(session_id=session_id, message=user_message)

        domain_messages = [
            Message(
                id=uuid4(),
                content=user_message,
                role='user',
                metadata={'timestamp': '2023-01-01T00:00:00Z'},
            ),
            Message(
                id=uuid4(),
                content='Response with metadata',
                role='assistant',
                metadata={'provider': 'langgraph', 'confidence': 0.95},
            ),
        ]
        ai_service.generate_response = AsyncMock(return_value=domain_messages)

        # act
        result = await chat(request, ai_service)

        # assert
        assert len(result.messages) == 2
        assert result.messages[0].metadata == {'timestamp': '2023-01-01T00:00:00Z'}
        assert result.messages[1].metadata == {'provider': 'langgraph', 'confidence': 0.95}

    async def test_chat_single_message_response(self, ai_service: AIService) -> None:
        # arrange
        session_id = uuid4()
        user_message = 'Quick question'
        request = ChatRequest(session_id=session_id, message=user_message)

        # AI service returns only assistant message
        domain_messages = [
            Message(id=uuid4(), content='Quick answer', role='assistant', metadata=None)
        ]
        ai_service.generate_response = AsyncMock(return_value=domain_messages)

        # act
        result = await chat(request, ai_service)

        # assert
        assert len(result.messages) == 1
        assert result.messages[0].role == 'assistant'
        assert result.messages[0].content == 'Quick answer'

    async def test_chat_multiple_assistant_messages(self, ai_service: AIService) -> None:
        # arrange
        session_id = uuid4()
        user_message = 'Complex question'
        request = ChatRequest(session_id=session_id, message=user_message)

        domain_messages = [
            Message(id=uuid4(), content=user_message, role='user', metadata=None),
            Message(id=uuid4(), content='First part of answer', role='assistant', metadata=None),
            Message(id=uuid4(), content='Second part of answer', role='assistant', metadata=None),
            Message(id=uuid4(), content='Final conclusion', role='assistant', metadata=None),
        ]
        ai_service.generate_response = AsyncMock(return_value=domain_messages)

        # act
        result = await chat(request, ai_service)

        # assert
        assert len(result.messages) == 4
        assert result.messages[0].role == 'user'
        assert result.messages[1].role == 'assistant'
        assert result.messages[2].role == 'assistant'
        assert result.messages[3].role == 'assistant'
        assert result.messages[1].content == 'First part of answer'
        assert result.messages[3].content == 'Final conclusion'

    async def test_chat_with_system_message(self, ai_service: AIService) -> None:
        # arrange
        session_id = uuid4()
        user_message = 'Help me'
        request = ChatRequest(session_id=session_id, message=user_message)

        domain_messages = [
            Message(id=uuid4(), content='System context loaded', role='system', metadata=None),
            Message(id=uuid4(), content=user_message, role='user', metadata=None),
            Message(id=uuid4(), content="I'm here to help!", role='assistant', metadata=None),
        ]
        ai_service.generate_response = AsyncMock(return_value=domain_messages)

        # act
        result = await chat(request, ai_service)

        # assert
        assert len(result.messages) == 3
        assert result.messages[0].role == 'system'
        assert result.messages[1].role == 'user'
        assert result.messages[2].role == 'assistant'

    async def test_message_schema_from_domain_model_conversion(
        self, ai_service: AIService
    ) -> None:
        # arrange
        session_id = uuid4()
        message_id = uuid4()
        request = ChatRequest(session_id=session_id, message='Test conversion')

        domain_message = Message(
            id=message_id,
            content='Test message',
            role='assistant',
            metadata={'test': 'value', 'number': 42},
        )
        ai_service.generate_response = AsyncMock(return_value=[domain_message])

        # act
        result = await chat(request, ai_service)

        # assert
        schema_message = result.messages[0]
        assert schema_message.id == message_id
        assert schema_message.content == 'Test message'
        assert schema_message.role == 'assistant'
        assert schema_message.metadata == {'test': 'value', 'number': 42}

    async def test_chat_preserves_message_ids(self, ai_service: AIService) -> None:
        # arrange
        session_id = uuid4()
        user_msg_id = uuid4()
        assistant_msg_id = uuid4()
        request = ChatRequest(session_id=session_id, message='Test ID preservation')

        domain_messages = [
            Message(id=user_msg_id, content='Test ID preservation', role='user', metadata=None),
            Message(id=assistant_msg_id, content='Response', role='assistant', metadata=None),
        ]
        ai_service.generate_response = AsyncMock(return_value=domain_messages)

        # act
        result = await chat(request, ai_service)

        # assert
        assert result.messages[0].id == user_msg_id
        assert result.messages[1].id == assistant_msg_id
