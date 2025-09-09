from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistant.db.dependencies import get_db_session
from ai_assistant.repository.session import SessionRepository
from ai_assistant.services.session import SessionService


def get_session_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SessionService:
    """
    FastAPI dependency to get a session service.

    Constructs the complete service dependency chain internally.
    API layer only knows about services, not repositories.

    Args:
        session: The database session from FastAPI dependency injection.

    Returns:
        SessionService: The configured session service.
    """
    repository = SessionRepository(session=session)
    return SessionService(session_repository=repository)
