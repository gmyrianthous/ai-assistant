from typing import Any
from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

from ai_assistant.domain import Content as DomainContent


class ChatRequest(BaseModel):
    message: str
    session_id: UUID
    user_id: UUID


class ContentResponse(BaseModel):
    """
    Content response schema.

    This is the unified response for both streaming and non-streaming endpoints.
    The 'type' field determines how clients should interpret the 'data' payload.

    Examples:
        ContentResponse(type='message', data={'text': 'Hello world'}, role='model')
        ContentResponse(type='loader', data={'message': 'Processing...', 'show_spinner': True})
        ContentResponse(type='metadata', data={}, metadata={'session_id': '...'})
    """

    id: UUID
    type: Literal['message', 'loader', 'metadata']
    data: dict[str, Any] = Field(description="Content data payload - structure depends on 'type'")
    role: str | None = Field(default=None, description="Role from ADK (e.g., 'user', 'model')")
    metadata: dict[str, Any] | None = Field(default=None, description='Additional metadata')

    @classmethod
    def from_domain_model(cls, content: DomainContent) -> 'ContentResponse':
        """
        Create ContentResponse from domain Content model.

        Args:
            content: Domain Content instance

        Returns:
            ContentResponse instance
        """
        return cls(
            id=content.id,
            type=content.type,
            data=content.data,
            role=content.role,
            metadata=content.metadata,
        )
