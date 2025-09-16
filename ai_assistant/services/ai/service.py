import logging
from collections.abc import AsyncGenerator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistant.services.ai.providers.base import AIProvider

logger = logging.getLogger(__name__)


class AIService:
    """
    This is framework-agnostic AI service, responsible for delegates AI operations to
    pluggable AI providers (LangGraph, OpenAI SDK, ADK, etc.).
    """

    def __init__(self, db_session: AsyncSession, provider: AIProvider) -> None:
        self.db_session = db_session
        self.provider = provider

    async def generate_response(self, session_id: UUID, user_message: str) -> str:
        """
        Generate AI response for the given user message.

        Args:
            session_id: The ID of the session
            user_message: The user message to generate a response for

        Returns:
            (str): The generated response
        """
        return await self.provider.generate_response(session_id, user_message)

    async def generate_stream_response(
        self,
        session_id: UUID,
        user_message: str,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response from AI.

        Args:
            session_id: The ID of the session
            user_message: The user message to generate a response for

        Yields:
            Chunks of the streaming response
        """
        async for chunk in self.provider.generate_stream_response(session_id, user_message):
            yield chunk

    async def cleanup(self) -> None:
        """Clean up AI service resources."""
        await self.provider.cleanup()
