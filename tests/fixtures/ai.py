"""General AI fixtures (Langfuse stub, mocks of the ADK runner) shared across tests.

This module is imported first by `tests.fixtures` (before any application
imports) so the Langfuse client can be stubbed out: agent modules fetch their
prompts from Langfuse at import time, which must not hit the network in tests.
"""

from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

import pytest
from google.adk.events import Event

from ai_assistant.common.clients import langfuse as _langfuse_module


def _install_langfuse_stub() -> None:
    """Seed the cached Langfuse client with a stub before app modules import."""
    stub_prompt = MagicMock()
    stub_prompt.prompt = 'You are a helpful assistant.'
    stub_prompt.config = {}

    stub_client = MagicMock()
    stub_client.get_prompt.return_value = stub_prompt

    _langfuse_module._langfuse_client = stub_client


_install_langfuse_stub()


@pytest.fixture
def mock_adk_runner() -> MagicMock:
    """
    Mock of the underlying ADK Runner.

    Use `mock_adk_runner.set_events([...])` to define the events yielded by
    `run_async`. Each call to `run_async` replays the configured events.
    """
    runner = MagicMock()

    def set_events(events: list[Event]) -> None:
        def run_async(*args: object, **kwargs: object) -> AsyncGenerator[Event, None]:
            async def generate() -> AsyncGenerator[Event, None]:
                for event in events:
                    yield event

            return generate()

        runner.run_async = MagicMock(side_effect=run_async)

    runner.set_events = set_events
    return runner
