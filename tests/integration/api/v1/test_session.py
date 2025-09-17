import uuid

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistant.api.main import app

client = TestClient(app)


class TestSessionPost:
    def test_create_session_success(self, db_session: AsyncSession) -> None:
        # arrange
        user_id = str(uuid.uuid4())
        request_payload = {'user_id': user_id}
        expected_status = 201
        expected_intro_message = 'Hello, how can I help you today?'

        # act
        result = client.post('/api/v1/chatbot/session', json=request_payload)

        # assert
        assert result.status_code == expected_status
        response_data = result.json()
        assert 'session_id' in response_data
        assert response_data['intro_message'] == expected_intro_message
        uuid.UUID(response_data['session_id'])

    def test_create_session_invalid_user_id(self, db_session: AsyncSession) -> None:
        # arrange
        invalid_user_id = 'not-a-valid-uuid'
        request_payload = {'user_id': invalid_user_id}
        expected_status = 422

        # act
        result = client.post('/api/v1/chatbot/session', json=request_payload)

        # assert
        assert result.status_code == expected_status

    def test_create_session_missing_user_id(self, db_session: AsyncSession) -> None:
        # arrange
        expected_status = 422

        # act
        result = client.post('/api/v1/chatbot/session', json={})

        # assert
        assert result.status_code == expected_status
