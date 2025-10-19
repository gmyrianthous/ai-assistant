from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from google.adk.events import Event
from google.adk.sessions import InMemorySessionService

from ai_assistant.services.ai.processors.registry import AgentProcessorRegistry
from ai_assistant.services.ai.runner import AgentRunner
from tests.factories import ADKEventFactory


class TestAgentRunner:
    @pytest.mark.asyncio
    async def test_weather_assistant_flow_with_tool_and_response(
        self,
        session_service: InMemorySessionService,
        mock_adk_runner: MagicMock,
        weather_assistant_events: list[Event],
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        message = 'What is the weather in Paris?'

        mock_adk_runner.set_events(weather_assistant_events)

        registry = AgentProcessorRegistry()
        runner = AgentRunner(
            session_service=session_service,
            processor_registry=registry,
        )

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            contents = []
            async for content in runner.run_stream(session_id, message, user_id):
                contents.append(content)

        # assert
        assert len(contents) == 3

        assert contents[0].type == 'loader'
        assert 'weather' in contents[0].data['message'].lower()
        assert contents[0].data['show_spinner'] is True

        assert contents[1].type == 'message'
        assert 'weather' in contents[1].data['text'].lower()

        assert contents[2].type == 'message'
        assert 'sunny' in contents[2].data['text'].lower()

        assert contents[0].id == contents[1].id == contents[2].id

        assert all(
            c.metadata is not None and c.metadata['session_id'] == str(session_id)
            for c in contents
        )

    @pytest.mark.asyncio
    async def test_recipe_assistant_flow_with_tool_and_response(
        self,
        session_service: InMemorySessionService,
        mock_adk_runner: MagicMock,
        recipe_assistant_events: list[Event],
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        message = 'How do I make chocolate cake?'

        mock_adk_runner.set_events(recipe_assistant_events)

        registry = AgentProcessorRegistry()
        runner = AgentRunner(
            session_service=session_service,
            processor_registry=registry,
        )

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            contents = []
            async for content in runner.run_stream(session_id, message, user_id):
                contents.append(content)

        # assert
        assert len(contents) == 3
        assert contents[0].type == 'loader'
        assert 'recipe' in contents[0].data['message'].lower()
        assert all(c.type == 'message' for c in contents[1:])

    @pytest.mark.asyncio
    async def test_orchestrator_flow_without_tools(
        self,
        session_service: InMemorySessionService,
        mock_adk_runner: MagicMock,
        orchestrator_events: list[Event],
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        message = 'Hello'

        mock_adk_runner.set_events(orchestrator_events)

        registry = AgentProcessorRegistry()
        runner = AgentRunner(
            session_service=session_service,
            processor_registry=registry,
        )

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            contents = []
            async for content in runner.run_stream(session_id, message, user_id):
                contents.append(content)

        # assert
        assert len(contents) == 2
        assert all(c.type == 'message' for c in contents)

    @pytest.mark.asyncio
    async def test_run_non_streaming_returns_final_message(
        self,
        session_service: InMemorySessionService,
        mock_adk_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        message = 'Hello'

        # Create final response event
        final_event = ADKEventFactory.final_response(
            'Complete response',
            author='orchestrator',
        )

        mock_adk_runner.set_events([final_event])

        runner = AgentRunner(session_service=session_service)

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            result = await runner.run(session_id, message, user_id)

        # assert
        assert result == 'Complete response'

    @pytest.mark.asyncio
    async def test_filters_user_events(
        self,
        session_service: InMemorySessionService,
        mock_adk_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        message = 'Hello'

        # Mix of user and agent events
        events = [
            ADKEventFactory.with_text('User message', author='user'),
            ADKEventFactory.with_text('Agent response', author='orchestrator'),
        ]

        mock_adk_runner.set_events(events)

        runner = AgentRunner(session_service=session_service)

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            contents = []
            async for content in runner.run_stream(session_id, message, user_id):
                contents.append(content)

        # assert
        assert len(contents) == 1
        assert contents[0].data['text'] == 'Agent response'

    @pytest.mark.asyncio
    async def test_multiple_agents_in_sequence(
        self,
        session_service: InMemorySessionService,
        mock_adk_runner: MagicMock,
    ) -> None:
        # arrange
        session_id = uuid4()
        user_id = uuid4()
        message = 'Tell me the weather and give me a recipe'

        # Orchestrator delegates to weather and recipe assistants
        events = [
            ADKEventFactory.with_text('Let me check', author='orchestrator'),
            ADKEventFactory.with_function_call('get_weather', author='weather_assistant'),
            ADKEventFactory.with_text('Weather is nice', author='weather_assistant'),
            ADKEventFactory.with_function_call('get_recipe', author='recipe_assistant'),
            ADKEventFactory.with_text('Here is a recipe', author='recipe_assistant'),
        ]

        mock_adk_runner.set_events(events)

        registry = AgentProcessorRegistry()
        runner = AgentRunner(session_service=session_service, processor_registry=registry)

        with patch.object(runner, '_get_adk_runner', return_value=mock_adk_runner):
            # act
            contents = []
            async for content in runner.run_stream(session_id, message, user_id):
                contents.append(content)

        # assert
        assert len(contents) == 5
        assert contents[0].type == 'message'
        assert contents[1].type == 'loader'
        assert contents[2].type == 'message'
        assert contents[3].type == 'loader'
        assert contents[4].type == 'message'
