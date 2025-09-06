from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Session(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime | None
    updated_at: datetime | None
    ended_at: datetime | None
