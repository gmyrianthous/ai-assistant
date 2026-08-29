from fastapi.testclient import TestClient

from ai_assistant.api.main import app

client = TestClient(app)


class TestChatUIGet:
    def test_serves_chat_page(self) -> None:
        # act
        result = client.get('/chat')

        # assert
        assert result.status_code == 200
        assert result.headers['content-type'].startswith('text/html')
        assert '/api/v1/chat' in result.text
