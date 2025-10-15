from typing import Any
from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from ai_assistant.domain import Message as DomainMessage


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message")
    session_id: UUID = Field(..., description='Session ID for continuing a conversation')
    user_id: UUID = Field(..., description='User ID for tracking conversations across sessions')


class MessageSchema(BaseModel):
    id: UUID
    content: str
    role: Literal['user', 'assistant']
    metadata: dict[str, Any] | None = None

    @field_validator('role', mode='before')
    @classmethod
    def normalize_role(cls, v: str) -> str:
        """Normalize role values from ADK to API schema."""
        role_mapping = {
            'model': 'assistant',
            'system': 'assistant',
        }
        return role_mapping.get(v, v)

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
