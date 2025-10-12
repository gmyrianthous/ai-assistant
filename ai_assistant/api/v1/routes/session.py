import uuid

from fastapi import APIRouter
from fastapi import Request
from fastapi import status

from ai_assistant.api.v1.schemas.session import SessionListItem
from ai_assistant.api.v1.schemas.session import SessionListResponse
from ai_assistant.api.v1.schemas.session import SessionRequest
from ai_assistant.api.v1.schemas.session import SessionResponse
from ai_assistant.common.settings import settings

router = APIRouter()


@router.post(
    '/session',
    status_code=status.HTTP_201_CREATED,
    summary='Create a new session',
)
async def create_session(body: SessionRequest, request: Request) -> SessionResponse:
    """
    Create a new session in the database.

    Args:
        body (SessionRequest): The session creation request containing user_id.
        request (Request): The FastAPI request object.

    Returns:
        (SessionResponse): The response with session details.
    """
    session = await request.app.state.session_service.create_session(
        user_id=str(body.user_id),
        app_name=settings.APP_NAME,
    )
    intro_message = 'Hello, how can I help you today?'

    return SessionResponse(session_id=session.id, intro_message=intro_message)


@router.get(
    '/sessions/{user_id}',
    status_code=status.HTTP_200_OK,
    summary='Get all sessions for a user',
)
async def get_user_sessions(user_id: uuid.UUID, request: Request) -> SessionListResponse:
    """
    Get all sessions for a specific user.

    Args:
        user_id (uuid.UUID): The ID of the user.
        request (Request): The FastAPI request object.

    Returns:
        (SessionListResponse): List of all sessions for the user.
    """
    sessions_response = await request.app.state.session_service.list_sessions(
        app_name=settings.APP_NAME,
        user_id=str(user_id),
    )

    session_items = [
        SessionListItem(
            session_id=session.id,
            user_id=session.user_id,
            app_name=session.app_name,
            state=session.state,
            last_update_time=session.last_update_time,
        )
        for session in sessions_response.sessions
    ]

    return SessionListResponse(sessions=session_items)
