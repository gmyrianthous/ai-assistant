from uuid import UUID

from sqlalchemy import select

from ai_assistant.domain import Session
from ai_assistant.models.session import Session as SessionModel
from ai_assistant.repository.abstract import AbstractRepository


class SessionRepository(AbstractRepository):
    model = SessionModel

    async def get_by_id(self, id: UUID, /) -> Session | None:
        """
        Get a session by its id.

        Args:
            id (UUID): The id of the session to get.

        Returns:
            (Session | None): The session if found, None otherwise.
        """
        query = select(self.model).filter(self.model.id == id)

        session_obj: SessionModel | None = (await self.session.execute(query)).scalar_one_or_none()

        if not session_obj:
            return None

        return Session.model_validate(session_obj, from_attributes=True)
