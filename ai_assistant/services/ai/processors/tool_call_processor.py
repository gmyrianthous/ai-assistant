import uuid
from collections.abc import Iterator

from google.adk.events import Event

from ai_assistant.domain import Content
from ai_assistant.services.ai.processors.base import BaseEventProcessor


class ToolCallProcessor(BaseEventProcessor):
    """Converts tool/function calls in ADK events into 'loader' Content objects."""

    def process_event(
        self,
        event: Event,
        session_id: uuid.UUID,
        message_id: uuid.UUID,
    ) -> Iterator[Content]:
        content = getattr(event, 'content', None)
        if content is None or not content.parts:
            return

        for part in content.parts:
            if part.function_call and part.function_call.name:
                yield Content(
                    id=message_id,
                    type='loader',
                    data={
                        'message': self._loader_message(part.function_call.name),
                        'show_spinner': True,
                    },
                    role=content.role,
                    metadata={'session_id': str(session_id)},
                )

    @staticmethod
    def _loader_message(function_name: str) -> str:
        """
        Build a human-readable loading message from a tool name.

        E.g. 'get_weather' -> 'Fetching weather...'
        """
        topic = function_name.removeprefix('get_').replace('_', ' ')
        return f'Fetching {topic}...'
