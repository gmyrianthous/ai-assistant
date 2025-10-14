from typing import Any
from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

from ai_assistant.domain import Message as DomainMessage


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message")
    session_id: str = Field(..., description='Session ID for continuing a conversation')
    user_id: str = Field(..., description='User ID for tracking conversations across sessions')


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
    session_id: str = Field(..., description='Session ID for this conversation')
    messages: list[MessageSchema] = Field(..., description='Messages in this exchange')


class ChatStreamChunk(BaseModel):
    content: str = Field(..., description='Content chunk')
    done: bool = Field(default=False, description='Whether this is the final chunk')
    metadata: dict[str, Any] | None = Field(default=None, description='Optional metadata')
