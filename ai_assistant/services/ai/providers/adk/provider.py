from collections.abc import AsyncGenerator
from uuid import UUID

from ai_assistant.domain import Message
from ai_assistant.services.ai.providers.base import AIProvider


class ADKProvider(AIProvider):
    async def generate_response(
        self,
        session_id: UUID,
        user_message: str,
    ) -> list[Message]:
        raise NotImplementedError

    async def generate_stream_response(
        self,
        session_id: UUID,
        user_message: str,
    ) -> AsyncGenerator[str, None]:
        raise NotImplementedError
