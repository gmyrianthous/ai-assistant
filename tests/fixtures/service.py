import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistant.repository.session import SessionRepository
from ai_assistant.services.session import SessionService


@pytest.fixture
def session_service(db_session: AsyncSession) -> SessionService:
    """
    Create a SessionService instance for testing.

    Args:
        db_session (AsyncSession): The test database session.

    Returns:
        (SessionService): The session service instance.
    """
    session_repository = SessionRepository(session=db_session)
    return SessionService(session_repository=session_repository)
