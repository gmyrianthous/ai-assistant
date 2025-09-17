from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport
from httpx import AsyncClient

from ai_assistant.api.main import app
from tests.fixtures.database import *  # noqa
from tests.fixtures.repository import *  # noqa


@pytest.fixture(scope='function')
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client
