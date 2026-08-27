import json
import uuid
from unittest.mock import MagicMock
from unittest.mock import patch

from fastapi.testclient import TestClient

from ai_assistant.api.main import app
from tests.factories import ADKEventFactory

client = TestClient(app)


def _run_agent_input(user_id: str, text: str) -> dict:
    """Build a minimal AG-UI RunAgentInput payload."""
    return {
        'threadId': str(uuid.uuid4()),
        'runId': str(uuid.uuid4()),
        'state': {},
        'messages': [{'id': str(uuid.uuid4()), 'role': 'user', 'content': text}],
        'tools': [],
        'context': [],
        'forwardedProps': {'user_id': user_id},
    }


class TestAGUIEndpoint:
    @patch('ag_ui_adk.adk_agent.Runner')
    def test_run_streams_agui_events(self, mock_runner_class: MagicMock) -> None:
        # arrange
        adk_events = [
            ADKEventFactory.with_text('Hello ', author='orchestrator'),
            ADKEventFactory.with_text('world!', author='orchestrator'),
            ADKEventFactory.final_response('Hello world!', author='orchestrator'),
        ]

        def run_async(**kwargs):
            async def generate():
                for event in adk_events:
                    yield event

            return generate()

        mock_runner = MagicMock()
        mock_runner.run_async = MagicMock(side_effect=run_async)
        mock_runner_class.return_value = mock_runner

        payload = _run_agent_input(user_id=str(uuid.uuid4()), text='Hi!')

        # act
        with client.stream(
            'POST',
            '/api/v1/agui',
            json=payload,
            headers={'Accept': 'text/event-stream'},
        ) as response:
            assert response.status_code == 200

            events = []
            for line in response.iter_lines():
                if line.startswith('data: '):
                    events.append(json.loads(line.removeprefix('data: ')))

        # assert
        event_types = [event['type'] for event in events]
        assert event_types[0] == 'RUN_STARTED'
        assert event_types[-1] == 'RUN_FINISHED'

        streamed_text = ''.join(
            event['delta'] for event in events if event['type'] == 'TEXT_MESSAGE_CONTENT'
        )
        assert 'Hello world!' in streamed_text
