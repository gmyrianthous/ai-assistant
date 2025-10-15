from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from google.adk.sessions import Session

from ai_assistant.api.v1.routes.session import create_session
from ai_assistant.api.v1.routes.session import get_session
from ai_assistant.api.v1.routes.session import get_user_sessions
from ai_assistant.api.v1.schemas.session import SessionDetailResponse
from ai_assistant.api.v1.schemas.session import SessionListResponse
from ai_assistant.api.v1.schemas.session import SessionRequest
from ai_assistant.api.v1.schemas.session import SessionResponse
from ai_assistant.exceptions import NotFoundException
from ai_assistant.services.ai.adk.session_factory import ADKSessionService


class TestCreateSession:
    async def test_create_session_success(self) -> None:
        # arrange
        session_service = AsyncMock(spec=ADKSessionService)
        user_id = uuid4()
        session_id = uuid4()
        request = SessionRequest(user_id=user_id)

        mock_session = MagicMock()
        mock_session.id = session_id
        session_service.create_session = AsyncMock(return_value=mock_session)

        # act
        result = await create_session(request, session_service)

        # assert
        assert isinstance(result, SessionResponse)
        assert result.session_id == session_id
        assert result.intro_message == 'Hello, how can I help you today?'
        session_service.create_session.assert_called_once()


class TestGetSession:
    async def test_get_session_success(self) -> None:
        # arrange
        session_service = AsyncMock(spec=ADKSessionService)
        session_id = str(uuid4())
        user_id = str(uuid4())

        mock_session = MagicMock(spec=Session)
        mock_session.id = session_id
        mock_session.user_id = user_id
        mock_session.app_name = 'test_app'
        mock_session.state = {}
        mock_session.events = []
        mock_session.last_update_time = 1234567890.0

        session_service.get_session = AsyncMock(return_value=mock_session)

        # act
        result = await get_session(session_id, user_id, session_service)

        # assert
        assert isinstance(result, SessionDetailResponse)
        assert result.session_id == session_id
        assert result.user_id == user_id
        assert result.messages == []
        session_service.get_session.assert_called_once()

    async def test_get_session_not_found(self) -> None:
        # arrange
        session_service = AsyncMock(spec=ADKSessionService)
        session_id = str(uuid4())
        user_id = str(uuid4())

        # Mock returns None, which should trigger NotFoundException in the endpoint
        session_service.get_session = AsyncMock(return_value=None)

        # act & assert
        with pytest.raises(NotFoundException) as exc_info:
            await get_session(session_id, user_id, session_service)

        assert f'Session {session_id} not found' in str(exc_info.value)


class TestGetUserSessions:
    async def test_get_user_sessions_success(self) -> None:
        # arrange
        session_service = AsyncMock(spec=ADKSessionService)
        user_id = uuid4()

        mock_session_1 = MagicMock()
        mock_session_1.id = str(uuid4())
        mock_session_1.user_id = str(user_id)
        mock_session_1.app_name = 'test_app'
        mock_session_1.state = {}
        mock_session_1.last_update_time = 1234567890.0

        mock_session_2 = MagicMock()
        mock_session_2.id = str(uuid4())
        mock_session_2.user_id = str(user_id)
        mock_session_2.app_name = 'test_app'
        mock_session_2.state = {}
        mock_session_2.last_update_time = 1234567891.0

        mock_response = MagicMock()
        mock_response.sessions = [mock_session_1, mock_session_2]

        session_service.list_sessions = AsyncMock(return_value=mock_response)

        # act
        result = await get_user_sessions(user_id, session_service)

        # assert
        assert isinstance(result, SessionListResponse)
        assert len(result.sessions) == 2
        assert result.sessions[0].session_id == mock_session_1.id
        assert result.sessions[1].session_id == mock_session_2.id
        session_service.list_sessions.assert_called_once()

    async def test_get_user_sessions_empty(self) -> None:
        # arrange
        session_service = AsyncMock(spec=ADKSessionService)
        user_id = uuid4()

        mock_response = MagicMock()
        mock_response.sessions = []

        session_service.list_sessions = AsyncMock(return_value=mock_response)

        # act
        result = await get_user_sessions(user_id, session_service)

        # assert
        assert isinstance(result, SessionListResponse)
        assert len(result.sessions) == 0
