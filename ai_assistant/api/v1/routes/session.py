import logging
import uuid
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from ai_assistant.api.dependencies import get_session_service
from ai_assistant.api.v1.schemas.chat import ContentResponse
from ai_assistant.api.v1.schemas.session import SessionDetailResponse
from ai_assistant.api.v1.schemas.session import SessionListItem
from ai_assistant.api.v1.schemas.session import SessionListResponse
from ai_assistant.api.v1.schemas.session import SessionRequest
from ai_assistant.api.v1.schemas.session import SessionResponse
from ai_assistant.common.settings import settings
from ai_assistant.exceptions import NotFoundException
from ai_assistant.services.ai.adk.session_factory import ADKSessionService

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post(
    '/session',
    status_code=status.HTTP_201_CREATED,
    summary='Create a new session',
)
async def create_session(
    body: SessionRequest,
    session_service: Annotated[ADKSessionService, Depends(get_session_service)],
) -> SessionResponse:
    """
    Create a new session in the database.

    Args:
        body (SessionRequest): The session creation request containing user_id.
        session_service (ADKSessionService): The injected session service.

    Returns:
        (SessionResponse): The response with session details.
    """
    logger.debug(f'Creating session for user {body.user_id}')
    session = await session_service.create_session(
        user_id=str(body.user_id),
        app_name=settings.APP_NAME,
    )
    intro_message = 'Hello, how can I help you today?'

    logger.debug(f'Session {session.id} created successfully for user {body.user_id}')
    return SessionResponse(session_id=uuid.UUID(session.id), intro_message=intro_message)


@router.get(
    '/sessions/{user_id}',
    status_code=status.HTTP_200_OK,
    summary='Get all sessions for a user',
)
async def get_user_sessions(
    user_id: uuid.UUID,
    session_service: Annotated[ADKSessionService, Depends(get_session_service)],
) -> SessionListResponse:
    """
    Get all sessions for a specific user.

    Args:
        user_id (uuid.UUID): The ID of the user.
        session_service (ADKSessionService): The injected session service.

    Returns:
        (SessionListResponse): List of all sessions for the user.
    """
    sessions_response = await session_service.list_sessions(
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


@router.get(
    '/session/{session_id}',
    status_code=status.HTTP_200_OK,
    summary='Get a specific session with all messages',
)
async def get_session(
    session_id: str,
    user_id: str,
    session_service: Annotated[ADKSessionService, Depends(get_session_service)],
) -> SessionDetailResponse:
    """
    Get a specific session with all its details including messages.

    Args:
        session_id (str): The ID of the session.
        user_id (str): The ID of the user.
        session_service (ADKSessionService): The injected session service.

    Returns:
        (SessionDetailResponse): The session details including all messages.
    """
    logger.debug(f'Retrieving session {session_id} for user {user_id}')

    session = await session_service.get_session(
        app_name=settings.APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    if not session:
        raise NotFoundException(f'Session {session_id} not found for user {user_id}')

    # Convert events to ContentResponse objects
    contents = []
    for event in session.events:
        if hasattr(event, 'content') and event.content:
            role = getattr(event.content, 'role', None)

            if hasattr(event.content, 'parts') and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        contents.append(
                            ContentResponse(
                                id=uuid.uuid4(),
                                type='message',
                                data={'text': part.text},
                                role=role,
                                metadata={'session_id': session_id},
                            )
                        )

    logger.debug(f'Retrieved session {session_id} with {len(contents)} contents')

    return SessionDetailResponse(
        session_id=session.id,
        user_id=session.user_id,
        app_name=session.app_name,
        state=session.state,
        contents=contents,
        last_update_time=session.last_update_time,
    )
