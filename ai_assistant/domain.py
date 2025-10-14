from typing import Any
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class Message(BaseModel):
    id: UUID
    content: str
    role: Literal['user', 'assistant']
    metadata: dict[str, Any] | None = None


class StreamChunk(BaseModel):
    id: UUID
    role: Literal['user', 'assistant'] = 'assistant'
    content: str
    metadata: dict[str, Any] | None = None
