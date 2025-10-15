import uuid
from unittest.mock import MagicMock
from unittest.mock import patch

from fastapi.testclient import TestClient
from google.genai.types import Content
from google.genai.types import Part

from ai_assistant.api.main import app

client = TestClient(app)


class TestChatPost:
    @patch('ai_assistant.services.ai.service.Runner')
    def test_chat_success(self, mock_runner_class: MagicMock) -> None:
        # arrange
        mock_event = MagicMock()
        mock_event.is_final_response.return_value = True
        mock_event.content = Content(
            role='model',
            parts=[Part(text='The weather in London is sunny with 20°C.')],
        )

        async def mock_run_async(*args, **kwargs):
            yield mock_event

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async = mock_run_async
        mock_runner_class.return_value = mock_runner_instance

        user_id = str(uuid.uuid4())
        session_response = client.post('/api/v1/chatbot/session', json={'user_id': user_id})
        session_id = session_response.json()['session_id']

        request_payload = {
            'message': 'What is the weather in London?',
            'session_id': session_id,
            'user_id': user_id,
        }
        expected_status = 200

        # act
        result = client.post('/api/v1/chatbot/chat', json=request_payload)

        # assert
        assert result.status_code == expected_status
        response_data = result.json()
        assert 'id' in response_data
        assert 'content' in response_data
        assert 'role' in response_data
        assert response_data['role'] == 'assistant'
        assert response_data['content'] == 'The weather in London is sunny with 20°C.'

    def test_chat_missing_message(self) -> None:
        # arrange
        user_id = str(uuid.uuid4())
        session_response = client.post('/api/v1/chatbot/session', json={'user_id': user_id})
        session_id = session_response.json()['session_id']

        request_payload = {
            'session_id': session_id,
            'user_id': user_id,
        }
        expected_status = 422

        # act
        result = client.post('/api/v1/chatbot/chat', json=request_payload)

        # assert
        assert result.status_code == expected_status

    def test_chat_missing_session_id(self) -> None:
        # arrange
        user_id = str(uuid.uuid4())
        request_payload = {
            'message': 'Hello',
            'user_id': user_id,
        }
        expected_status = 422

        # act
        result = client.post('/api/v1/chatbot/chat', json=request_payload)

        # assert
        assert result.status_code == expected_status

    def test_chat_missing_user_id(self) -> None:
        # arrange
        session_id = str(uuid.uuid4())
        request_payload = {
            'message': 'Hello',
            'session_id': session_id,
        }
        expected_status = 422

        # act
        result = client.post('/api/v1/chatbot/chat', json=request_payload)

        # assert
        assert result.status_code == expected_status


class TestChatStreamPost:
    @patch('ai_assistant.services.ai.service.Runner')
    def test_chat_stream_success(self, mock_runner_class: MagicMock) -> None:
        # arrange
        mock_events = [
            MagicMock(
                is_final_response=lambda: False,
                content=Content(role='model', parts=[Part(text='The ')]),
            ),
            MagicMock(
                is_final_response=lambda: False,
                content=Content(role='model', parts=[Part(text='weather ')]),
            ),
            MagicMock(
                is_final_response=lambda: True,
                content=Content(role='model', parts=[Part(text='is sunny.')]),
            ),
        ]

        async def mock_run_async(*args, **kwargs):
            for event in mock_events:
                yield event

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async = mock_run_async
        mock_runner_class.return_value = mock_runner_instance
        # arrange
        user_id = str(uuid.uuid4())
        session_response = client.post('/api/v1/chatbot/session', json={'user_id': user_id})
        session_id = session_response.json()['session_id']

        request_payload = {
            'message': 'What is the weather in Paris?',
            'session_id': session_id,
            'user_id': user_id,
        }
        expected_status = 200

        # act
        with client.stream('POST', '/api/v1/chatbot/chat/stream', json=request_payload) as result:
            # assert
            assert result.status_code == expected_status
            assert result.headers['content-type'] == 'text/event-stream; charset=utf-8'

            # Collect all chunks
            chunks = []
            for line in result.iter_lines():
                if line.startswith('data: '):
                    chunks.append(line)

            # Verify we received chunks (3 content + 1 metadata chunk)
            assert len(chunks) == 4

            # Verify last chunk has metadata
            import json

            last_chunk_data = json.loads(chunks[-1].replace('data: ', ''))
            assert 'metadata' in last_chunk_data
            assert last_chunk_data['metadata']['session_id'] == session_id

    def test_chat_stream_missing_message(self) -> None:
        # arrange
        user_id = str(uuid.uuid4())
        session_response = client.post('/api/v1/chatbot/session', json={'user_id': user_id})
        session_id = session_response.json()['session_id']

        request_payload = {
            'session_id': session_id,
            'user_id': user_id,
        }
        expected_status = 422

        # act
        result = client.post('/api/v1/chatbot/chat/stream', json=request_payload)

        # assert
        assert result.status_code == expected_status

    def test_chat_stream_missing_session_id(self) -> None:
        # arrange
        user_id = str(uuid.uuid4())
        request_payload = {
            'message': 'Hello',
            'user_id': user_id,
        }
        expected_status = 422

        # act
        result = client.post('/api/v1/chatbot/chat/stream', json=request_payload)

        # assert
        assert result.status_code == expected_status

    def test_chat_stream_missing_user_id(self) -> None:
        # arrange
        session_id = str(uuid.uuid4())
        request_payload = {
            'message': 'Hello',
            'session_id': session_id,
        }
        expected_status = 422

        # act
        result = client.post('/api/v1/chatbot/chat/stream', json=request_payload)

        # assert
        assert result.status_code == expected_status
