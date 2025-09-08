import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistant.repository.session import SessionRepository


@pytest.fixture
def session_repository(db_session: AsyncSession) -> SessionRepository:
    return SessionRepository(session=db_session)
