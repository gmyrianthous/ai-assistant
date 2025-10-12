from typing import Any
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class Message(BaseModel):
    id: UUID
    content: str
    role: Literal['user', 'assistant', 'system']
    metadata: dict[str, Any] | None = None
