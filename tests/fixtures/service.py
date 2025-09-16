from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistant.repository.session import SessionRepository
from ai_assistant.services.ai.providers.base import AIProvider
from ai_assistant.services.ai.service import AIService
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


@pytest.fixture
def ai_provider() -> AIProvider:
    provider = Mock(spec=AIProvider)
    provider.generate_response = AsyncMock()
    provider.generate_stream_response = Mock()
    provider.cleanup = AsyncMock()
    return provider


@pytest.fixture
def ai_service(db_session: AsyncSession, ai_provider: AIProvider) -> AIService:
    """
    Create an AIService instance for testing.

    Args:
        db_session (AsyncSession): The test database session.
        ai_provider (Mock): The mock AI provider.

    Returns:
        (AIService): The AI service instance.
    """
    return AIService(db_session=db_session, provider=ai_provider)
