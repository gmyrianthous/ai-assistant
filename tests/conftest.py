import pytest
from alembic.config import Config

from tests.fixtures.database import *  # noqa: F403


@pytest.fixture
def alembic_runner_config(alembic_config: Config) -> Config:
    """
    Configure pytest-alembic to use our test database.
    """
    return alembic_config
