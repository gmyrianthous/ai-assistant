from typing import Any
from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class Content(BaseModel):
    """
    Unified content model for all AI responses (streaming and non-streaming).

    The 'type' field determines how the client should interpret 'data'.
    This allows unlimited extensibility without changing the schema.

    Examples:
        # Text message
        Content(
            type="message",
            data={"text": "Hello world"}
        )

        # Loading indicator
        Content(
            type="loader",
            data={"message": "Checking weather...", "show_spinner": True}
        )

        # Metadata only (stream completion)
        Content(
            type="metadata",
            data={},
            metadata={"session_id": "..."}
        )
    """

    id: UUID
    type: Literal['message', 'loader', 'metadata'] = Field(
        description='Content type that determines how to render this content.'
    )
    data: dict[str, Any] = Field(description="Flexible data payload. Structure depends on 'type'.")
    metadata: dict[str, Any] | None = Field(
        default=None, description='Additional metadata (session_id, timestamps, etc.)'
    )
