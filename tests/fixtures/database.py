from collections.abc import AsyncIterator
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from pydantic import PostgresDsn
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from testcontainers.core.waiting_utils import wait_container_is_ready
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.postgres import PostgresContainer

from ai_assistant.db import database

_DATABASE_CONTAINER = 'postgres:17-alpine'
_DATABASE_DRIVER = 'asyncpg'


@pytest.fixture(scope='session')
@wait_container_is_ready()
def db_container() -> Iterator[PostgresContainer]:
    with PostgresContainer(_DATABASE_CONTAINER, driver=_DATABASE_DRIVER) as container:
        yield container


@pytest.fixture(scope='session')
async def db_url(db_container: PostgresContainer) -> PostgresDsn:  # type: ignore[no-any-unimported]
    """
    Get the URL of the db, start the container if needed
    """
    wait_for_logs(db_container, 'database system is ready to accept connections')

    return PostgresDsn(db_container.get_connection_url())


@pytest.fixture(scope='session')
def alembic_config(db_url: PostgresDsn) -> Config:
    """Create Alembic configuration for tests."""
    alembic_config_path = Path(__file__).parent / '../../alembic.ini'
    config = Config(alembic_config_path)
    config.set_main_option('sqlalchemy.url', str(db_url))
    config.set_main_option('loggers.keys', '')

    return config


@pytest.fixture(scope='session', autouse=True)
def run_migrations(alembic_config: Config) -> None:
    config = alembic_config
    command.upgrade(config, 'head')


@pytest.fixture(scope='function')
async def db_session(db_url: PostgresDsn, mocker: MockerFixture) -> AsyncIterator[AsyncSession]:
    async with database.db_session(db_url) as session:
        session.commit = mocker.AsyncMock(return_value=None)  # type: ignore[method-assign]
        session.close = mocker.AsyncMock(return_value=None)  # type: ignore[method-assign]
        mocker.patch('ai_assistant.db.database.get_session', mocker.Mock(return_value=session))

        await session.begin()

        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.rollback()
