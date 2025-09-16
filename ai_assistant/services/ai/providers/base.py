from abc import ABC
from abc import abstractmethod
from collections.abc import AsyncGenerator
from uuid import UUID


class AIProvider(ABC):

    @abstractmethod
    async def generate_response(self, session_id: UUID, user_message: str) -> str:
        """
        Generate AI response for the given user message.

        Args:
            session_id: The ID of the session
            user_message: The user message to generate a response for

        Returns:
            The generated response
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
