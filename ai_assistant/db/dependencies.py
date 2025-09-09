from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistant.db.database import db_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session for dependency injection.

    This is a framework-agnostic database dependency that can be used
    in FastAPI, CLI tools, background jobs, or any other context.

    Yields:
        AsyncSession: The database session.
    """
    async with db_session() as session:
        yield session
