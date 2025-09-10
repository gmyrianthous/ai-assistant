import uuid
from datetime import datetime
from datetime import timezone
from unittest.mock import AsyncMock

import freezegun
import pytest

from ai_assistant.domain import Session
from ai_assistant.exceptions import NotFoundException
from ai_assistant.services.session import SessionService


@freezegun.freeze_time('2025-01-01 00:00:00')
class TestSessionService:
    async def test_create_session_success(self) -> None:
        # arrange
        user_id = uuid.uuid4()
        session_id = uuid.uuid4()
        expected_session = Session(
            id=session_id,
            user_id=user_id,
            created_at= datetime.now(timezone.utc),
            updated_at= datetime.now(timezone.utc),
            ended_at=None,
        )

        mock_repository = AsyncMock()
        mock_repository.create.return_value = expected_session

        service = SessionService(session_repository=mock_repository)

        # act
        result = await service.create_session(user_id)

        # assert
        assert result == expected_session
        mock_repository.create.assert_called_once_with(user_id)

    @freezegun.freeze_time('2025-01-01 00:00:00')
    async def test_get_session_success(self) -> None:
        # arrange
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        expected_session = Session(
            id=session_id,
            user_id=user_id,
            created_at= datetime.now(timezone.utc),
            updated_at= datetime.now(timezone.utc),
            ended_at=None,
        )

        mock_repository = AsyncMock()
        mock_repository.get_by_id.return_value = expected_session

        service = SessionService(session_repository=mock_repository)

        # act
        result = await service.get_session(session_id)

        # assert
        assert result == expected_session
        mock_repository.get_by_id.assert_called_once_with(session_id)

    async def test_get_session_not_found(self) -> None:
        # arrange
        session_id = uuid.uuid4()

        mock_repository = AsyncMock()
        mock_repository.get_by_id.return_value = None

        service = SessionService(session_repository=mock_repository)

        # act & assert
        with pytest.raises(NotFoundException) as exc_info:
            await service.get_session(session_id)

        assert f'Session with ID {session_id} not found' in str(exc_info.value)
        mock_repository.get_by_id.assert_called_once_with(session_id)
