import uuid

from fastapi.testclient import TestClient

from ai_assistant.api.main import app

client = TestClient(app)


class TestSessionPost:
    def test_create_session_success(self) -> None:
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

    def test_create_session_invalid_user_id(self) -> None:
        # arrange
        invalid_user_id = 'not-a-valid-uuid'
        request_payload = {'user_id': invalid_user_id}
        expected_status = 422

        # act
        result = client.post('/api/v1/chatbot/session', json=request_payload)

        # assert
        assert result.status_code == expected_status

    def test_create_session_missing_user_id(self) -> None:
        # arrange
        expected_status = 422

        # act
        result = client.post('/api/v1/chatbot/session', json={})

        # assert
        assert result.status_code == expected_status


class TestSessionGet:
    def test_get_session_success(self) -> None:
        # arrange
        user_id = str(uuid.uuid4())
        session_response = client.post('/api/v1/chatbot/session', json={'user_id': user_id})
        session_id = session_response.json()['session_id']

        chat_payload = {
            'message': 'Hello',
            'session_id': session_id,
            'user_id': user_id,
        }
        client.post('/api/v1/chatbot/chat', json=chat_payload)

        # act
        result = client.get(
            f'/api/v1/chatbot/session/{session_id}',
            params={'user_id': user_id},
        )

        # assert
        assert result.status_code == 200
        response_data = result.json()
        assert response_data['session_id'] == session_id
        assert response_data['user_id'] == user_id
        assert 'contents' in response_data
        assert isinstance(response_data['contents'], list)
        assert 'last_update_time' in response_data

    def test_get_session_not_found(self) -> None:
        # arrange
        user_id = str(uuid.uuid4())
        non_existent_session_id = str(uuid.uuid4())

        # act
        result = client.get(
            f'/api/v1/chatbot/session/{non_existent_session_id}',
            params={'user_id': user_id},
        )

        # assert
        assert result.status_code == 404

    def test_get_session_missing_user_id(self) -> None:
        # arrange
        session_id = str(uuid.uuid4())

        # act
        result = client.get(f'/api/v1/chatbot/session/{session_id}')

        # assert
        assert result.status_code == 422


class TestSessionsList:
    def test_get_user_sessions_success(self) -> None:
        # arrange
        user_id = str(uuid.uuid4())
        session_1 = client.post('/api/v1/chatbot/session', json={'user_id': user_id})
        session_2 = client.post('/api/v1/chatbot/session', json={'user_id': user_id})

        session_id_1 = session_1.json()['session_id']
        session_id_2 = session_2.json()['session_id']

        # act
        result = client.get(f'/api/v1/chatbot/sessions/{user_id}')

        # assert
        assert result.status_code == 200
        response_data = result.json()
        assert 'sessions' in response_data
        assert isinstance(response_data['sessions'], list)
        assert len(response_data['sessions']) == 2

        session_ids = [s['session_id'] for s in response_data['sessions']]
        assert session_id_1 in session_ids
        assert session_id_2 in session_ids

    def test_get_user_sessions_no_sessions(self) -> None:
        # arrange
        user_id = str(uuid.uuid4())

        # act
        result = client.get(f'/api/v1/chatbot/sessions/{user_id}')

        # assert
        assert result.status_code == 200
        response_data = result.json()
        assert 'sessions' in response_data
        assert response_data['sessions'] == []

    def test_get_user_sessions_invalid_user_id(self) -> None:
        # arrange
        invalid_user_id = 'not-a-valid-uuid'

        # act
        result = client.get(f'/api/v1/chatbot/sessions/{invalid_user_id}')

        # assert
        assert result.status_code == 422
