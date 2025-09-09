import uuid

import pytest

from ai_assistant.exceptions import NotFoundException
from ai_assistant.services.session import SessionService


class TestSessionServiceIntegration:
    async def test_create_session_success(
        self, session_service: SessionService
    ) -> None:
        # arrange
        user_id = uuid.uuid4()

        # act
        created_session = await session_service.create_session(user_id)

        # assert
        assert created_session.id is not None
        assert created_session.user_id == user_id
        assert created_session.created_at is not None
        assert created_session.updated_at is not None
        assert created_session.ended_at is None


    async def test_get_session_success(self, session_service: SessionService) -> None:
        # arrange
        user_id = uuid.uuid4()
        test_session = await session_service.create_session(user_id)

        # act
        retrieved_session = await session_service.get_session(test_session.id)

        # assert
        assert retrieved_session.id == test_session.id
        assert retrieved_session.user_id == test_session.user_id
        assert retrieved_session.created_at == test_session.created_at
        assert retrieved_session.updated_at == test_session.updated_at
        assert retrieved_session.ended_at == test_session.ended_at


    async def test_get_nonexistent_session(self, session_service: SessionService) -> None:
        # arrange
        nonexistent_id = uuid.uuid4()

        # assert
        with pytest.raises(NotFoundException) as exc_info:
            # act
            await session_service.get_session(nonexistent_id)

        assert f'Session with ID {nonexistent_id} not found' in str(exc_info.value)
