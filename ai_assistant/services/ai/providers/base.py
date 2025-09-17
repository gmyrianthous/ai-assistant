from abc import ABC
from abc import abstractmethod
from collections.abc import AsyncGenerator
from uuid import UUID

from ai_assistant.domain import Message


class AIProvider(ABC):
    @abstractmethod
    async def generate_response(self, session_id: UUID, user_message: str) -> list[Message]:
        """
        Generate AI response for the given user message.

        Args:
            session_id: The ID of the session
            user_message: The user message to generate a response for

        Returns:
            List of messages including user message and AI response(s)
        """
        pass

    @abstractmethod
    async def generate_stream_response(
        self,
        session_id: UUID,
        user_message: str,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming AI response for the given user message.

        Args:
            session_id: The ID of the session
            user_message: The user message to generate a response for

        Yields:
            Chunks of the streaming response
        """
        pass
