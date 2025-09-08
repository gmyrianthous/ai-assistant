from ai_assistant.repository.session import SessionRepository
from tests.fixtures.factory.session import SessionFactory


class TestSessionRepository:
    async def test_get_by_id(self, session_repository: SessionRepository) -> None:
        # arrange
        session = SessionFactory.build()
        test_session = await session_repository.create(session.user_id)

        # act
        result = await session_repository.get_by_id(test_session.id)

        # assert
        assert result is not None
        assert result.id == test_session.id
        assert result.user_id == test_session.user_id
        assert result.created_at == test_session.created_at
        assert result.updated_at == test_session.updated_at
        assert result.ended_at == test_session.ended_at
