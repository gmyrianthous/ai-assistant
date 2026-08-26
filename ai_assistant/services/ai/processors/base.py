import uuid
from abc import ABC
from abc import abstractmethod
from collections.abc import Iterator

from google.adk.events import Event

from ai_assistant.domain import Content


class BaseEventProcessor(ABC):
    """
    Base class for ADK event processors.

    A processor inspects a raw ADK event and yields zero or more Content
    objects for the client (e.g. text messages, loading indicators).
    """

    @abstractmethod
    def process_event(
        self,
        event: Event,
        session_id: uuid.UUID,
        message_id: uuid.UUID,
    ) -> Iterator[Content]:
        """
        Process a single ADK event into client-facing Content objects.

        Args:
            event: Raw ADK event emitted by an agent.
            session_id: Conversation session ID.
            message_id: ID shared by all Content produced for one agent turn.

        Yields:
            Content: Processed content objects.
        """
