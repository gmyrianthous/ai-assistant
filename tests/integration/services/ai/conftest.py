"""Fixtures specific to AI service integration tests.

These fixtures provide sample event data for testing different agent scenarios.
General AI fixtures (mocks, session services) are in tests/fixtures/ai.py.
"""

import pytest
from google.adk.events import Event

from tests.factories import ADKEventFactory


@pytest.fixture
def weather_assistant_events() -> list[Event]:
    """
    Sample events from weather assistant for testing.

    Returns a list of events simulating a weather query:
    1. Function call to get_weather
    2-3. Text response parts streamed back
    """
    return [
        ADKEventFactory.with_function_call('get_weather', author='weather_assistant'),
        ADKEventFactory.with_text('The weather in ', author='weather_assistant'),
        ADKEventFactory.with_text('Paris is sunny.', author='weather_assistant'),
    ]


@pytest.fixture
def recipe_assistant_events():
    """
    Sample events from recipe assistant for testing.

    Returns a list of events simulating a recipe query:
    1. Function call to get_recipe
    2-3. Text response parts streamed back
    """
    return [
        ADKEventFactory.with_function_call('get_recipe', author='recipe_assistant'),
        ADKEventFactory.with_text('Here is a recipe for ', author='recipe_assistant'),
        ADKEventFactory.with_text('chocolate cake.', author='recipe_assistant'),
    ]


@pytest.fixture
def orchestrator_events():
    """
    Sample events from orchestrator for testing.

    Returns a list of events simulating orchestrator coordination:
    1-2. Text response parts (no tool calls)
    """
    return [
        ADKEventFactory.with_text('Hello from ', author='orchestrator'),
        ADKEventFactory.with_text('orchestrator.', author='orchestrator'),
    ]
