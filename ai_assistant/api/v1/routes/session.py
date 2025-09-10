from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from ai_assistant.api.dependencies import get_session_service
from ai_assistant.api.v1.schemas.session import SessionRequest
from ai_assistant.api.v1.schemas.session import SessionResponse
from ai_assistant.services.session import SessionService

router = APIRouter()


@router.post(
    '/session',
    status_code=status.HTTP_201_CREATED,
    summary='Create a new session',
)
async def create_session(
    request: SessionRequest,
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionResponse:
    """
    Create a new session in the database.

    Args:
        request (SessionRequest): The session creation request containing user_id.
        session_service (SessionService): The injected session service.

    Returns:
        (SessionResponse): The response with session details.
    """
    session = await session_service.create_session(request.user_id)
    intro_message = 'Hello, how can I help you today?'

    return SessionResponse(session_id=session.id, intro_message=intro_message)
