from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TestDatabaseConnection:
    async def test_can_execute_queries(self, db_session: AsyncSession) -> None:
        result = await db_session.execute(select(1))
        assert 1 == result.scalar_one()
