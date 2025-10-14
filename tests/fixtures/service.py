import pytest
from google.adk.sessions import InMemorySessionService

from ai_assistant.api.dependencies import get_session_service
from ai_assistant.api.main import app
from ai_assistant.services.ai.adk import session_factory


@pytest.fixture(scope='function', autouse=True)
def override_session_service():
    session_factory._session_service = None
    test_session_service = InMemorySessionService()
    app.dependency_overrides[get_session_service] = lambda: test_session_service

    yield test_session_service

    app.dependency_overrides.clear()
    session_factory._session_service = None
