import uuid

from fastapi import APIRouter
from fastapi import status

from ai_assistant.api.schemas.session import SessionRequest
from ai_assistant.api.schemas.session import SessionResponse

router = APIRouter()


@router.post(
    'v1/session',
    status_code=status.HTTP_200_OK,
    summary='Create a new session',
)
async def create_session(request: SessionRequest) -> SessionResponse:
    """
    Create a new session.

    Returns:
        SessionResponse: The response from the AI assistant.
    """
    session_id = uuid.uuid4()
    intro_message = 'Hello, how can I help you today?'

    return SessionResponse(
        session_id=session_id,
        intro_message=intro_message,
    )
