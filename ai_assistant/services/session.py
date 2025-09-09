import logging
from uuid import UUID

from ai_assistant.domain import Session
from ai_assistant.exceptions import NotFoundException
from ai_assistant.repository.session import SessionRepository

logger = logging.getLogger(__name__)


class SessionService:
    """
    Service layer for session business logic.

    This service handles session-related operations and coordinates
    between the API layer and the repository layer.
    """

    def __init__(self, session_repository: SessionRepository):
        self.session_repository = session_repository

    async def create_session(self, user_id: UUID) -> Session:
        """
        Create a new session for a user.

        Args:
            user_id (UUID): The ID of the user to create a session for.

        Returns:
            Session: The created session.
        """
        logger.info(f'Creating new session for user {user_id}')

        session = await self.session_repository.create(user_id)

        logger.info(f'Successfully created session {session.id} for user {user_id}')
        return session

    async def get_session(self, session_id: UUID) -> Session:
        """
        Retrieve a session by its ID.

        Args:
            session_id (UUID): The ID of the session to retrieve.

        Returns:
            Session: The retrieved session.

        Raises:
            NotFoundException: If the session is not found.
        """
        logger.info(f'Retrieving session {session_id}')

        session = await self.session_repository.get_by_id(session_id)

        if not session:
            logger.warning(f'Session {session_id} not found')
            raise NotFoundException(f'Session with ID {session_id} not found')

        logger.info(f'Successfully retrieved session {session_id}')
        return session
