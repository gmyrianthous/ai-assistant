import uuid
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from ai_assistant.api.dependencies import get_ai_service
from ai_assistant.api.main import app
from ai_assistant.domain import Message
from ai_assistant.services.ai.service import AIService


class TestChatEndpoint:
    async def test_chat_success(self, test_client: AsyncClient, ai_service: AIService) -> None:
        # arrange
        session_id = str(uuid.uuid4())
        user_message = 'Hello, AI assistant!'
        request_payload = {'session_id': session_id, 'message': user_message}
        expected_status = 200

        # Mock AI service response
        domain_messages = [
            Message(
                id=uuid.uuid4(),
                content=user_message,
                role='user',
                metadata=None,
            ),
            Message(
                id=uuid.uuid4(),
                content='Hello! How can I help you today?',
                role='assistant',
                metadata={'provider': 'test', 'session_id': session_id},
            ),
        ]
        ai_service.generate_response = AsyncMock(return_value=domain_messages)

        app.dependency_overrides[get_ai_service] = lambda: ai_service

        # act
        result = await test_client.post('/api/v1/chatbot/chat', json=request_payload)

        # cleanup
        app.dependency_overrides.clear()

        # assert
        assert result.status_code == expected_status
        response_data = result.json()
        assert 'messages' in response_data
        assert len(response_data['messages']) == 2

        user_msg = response_data['messages'][0]
        assert user_msg['content'] == user_message
        assert user_msg['role'] == 'user'
        assert user_msg['metadata'] is None
        uuid.UUID(user_msg['id'])

        assistant_msg = response_data['messages'][1]
        assert assistant_msg['content'] == 'Hello! How can I help you today?'
        assert assistant_msg['role'] == 'assistant'
        assert assistant_msg['metadata']['provider'] == 'test'
        assert assistant_msg['metadata']['session_id'] == session_id
        uuid.UUID(assistant_msg['id'])  # Validate UUID format

    async def test_chat_invalid_session_id(self, test_client: AsyncClient) -> None:
        # arrange
        invalid_session_id = 'not-a-valid-uuid'
        request_payload = {'session_id': invalid_session_id, 'message': 'Hello'}
        expected_status = 422

        # act
        result = await test_client.post('/api/v1/chatbot/chat', json=request_payload)
        response_data = result.json()

        # assert
        assert result.status_code == expected_status
        assert 'detail' in response_data

    @pytest.mark.parametrize(
        'request_payload',
        [
            pytest.param({'message': 'Hello'}, id='missing session_id'),
            pytest.param({'session_id': str(uuid.uuid4())}, id='missing message'),
            pytest.param({'session_id': 'invalidId', 'message': 'Hello'}, id='invalid session_id'),
        ],
    )
    async def test_chat_invalid_request_payload(
        self,
        test_client: AsyncClient,
        request_payload: dict,
    ) -> None:
        # arrange
        expected_status = 422

        # act
        result = await test_client.post('/api/v1/chatbot/chat', json=request_payload)

        # assert
        assert result.status_code == expected_status

    async def test_chat_missing_message(self, test_client: AsyncClient) -> None:
        # arrange
        session_id = str(uuid.uuid4())
        request_payload = {'session_id': session_id}
        expected_status = 422

        # act
        result = await test_client.post('/api/v1/chatbot/chat', json=request_payload)

        # assert
        assert result.status_code == expected_status
