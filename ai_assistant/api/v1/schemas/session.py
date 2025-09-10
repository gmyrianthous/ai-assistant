import uuid

from pydantic import BaseModel


class SessionRequest(BaseModel):
    user_id: uuid.UUID


class SessionResponse(BaseModel):
    session_id: uuid.UUID
    intro_message: str
