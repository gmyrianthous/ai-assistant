from fastapi.testclient import TestClient

from ai_assistant.api.main import app

client = TestClient(app)


class TestHealthGet:
    def test_status_and_response_ok(self) -> None:
        # arrange
        expected_status = 200
        expected_response = {'status': 'OK'}

        # act
        result = client.get('/health')

        # assert
        assert result.status_code == expected_status
        assert result.json() == expected_response
