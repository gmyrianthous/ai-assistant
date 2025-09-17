from typing import Any
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from ai_assistant.domain import Message as DomainMessage


class ChatRequest(BaseModel):
    session_id: UUID
    message: str


class MessageSchema(BaseModel):
    id: UUID
    content: str
    role: Literal['user', 'assistant', 'system']
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_domain_model(cls, domain_message: DomainMessage) -> 'MessageSchema':
        """
        Create MessageSchema from domain Message model.

        Args:
            domain_message: Domain Message instance

        Returns:
            MessageSchema instance
        """
        return cls(
            id=domain_message.id,
            content=domain_message.content,
            role=domain_message.role,
            metadata=domain_message.metadata,
        )


class ChatResponse(BaseModel):
    messages: list[MessageSchema]


class ChatStreamResponse(BaseModel):
    message_id: UUID
    content: str
    done: bool = False
    metadata: dict[str, Any] | None = None
