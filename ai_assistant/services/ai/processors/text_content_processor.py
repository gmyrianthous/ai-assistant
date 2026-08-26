import uuid
from collections.abc import Iterator

from google.adk.events import Event

from ai_assistant.domain import Content
from ai_assistant.services.ai.processors.base import BaseEventProcessor


class TextContentProcessor(BaseEventProcessor):
    """Converts text parts of ADK events into 'message' Content objects."""

    def process_event(
        self,
        event: Event,
        session_id: uuid.UUID,
        message_id: uuid.UUID,
    ) -> Iterator[Content]:
        # Skip final responses: in SSE streaming mode the final event repeats
        # the full text already delivered through the partial events.
        if event.is_final_response():
            return

        content = getattr(event, 'content', None)
        if content is None or not content.parts:
            return

        for part in content.parts:
            if part.text:
                yield Content(
                    id=message_id,
                    type='message',
                    data={'text': part.text},
                    role=content.role,
                    metadata={'session_id': str(session_id)},
                )
