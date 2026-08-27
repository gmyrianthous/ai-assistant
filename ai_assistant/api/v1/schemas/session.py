import uuid
from typing import Any

from pydantic import BaseModel


class SessionRequest(BaseModel):
    user_id: uuid.UUID


class SessionResponse(BaseModel):
    session_id: uuid.UUID
    intro_message: str


class SessionMessage(BaseModel):
    text: str
    role: str | None = None


class SessionDetailResponse(BaseModel):
    session_id: str
    user_id: str
    app_name: str
    state: dict[str, Any]
    contents: list[SessionMessage]
    last_update_time: float


class SessionListItem(BaseModel):
    session_id: str
    user_id: str
    app_name: str
    state: dict[str, Any]
    last_update_time: float


class SessionListResponse(BaseModel):
    sessions: list[SessionListItem]
