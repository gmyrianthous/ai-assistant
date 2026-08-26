import logging

from ai_assistant.services.ai.processors.base import BaseEventProcessor
from ai_assistant.services.ai.processors.text_content_processor import TextContentProcessor
from ai_assistant.services.ai.processors.tool_call_processor import ToolCallProcessor

logger = logging.getLogger(__name__)


class AgentProcessorRegistry:
    """
    Registry mapping agent names to their event processor pipelines.

    Agents without an explicitly registered pipeline fall back to the
    default pipeline (tool call loaders + text messages).
    """

    def __init__(self) -> None:
        self._default_pipeline: list[BaseEventProcessor] = [
            ToolCallProcessor(),
            TextContentProcessor(),
        ]
        self._pipelines: dict[str, list[BaseEventProcessor]] = {}

    def register(self, agent_name: str, processors: list[BaseEventProcessor]) -> None:
        """
        Register a custom processor pipeline for an agent.

        Args:
            agent_name: Name of the agent (ADK event author).
            processors: Processors applied, in order, to the agent's events.
        """
        logger.debug(f'Registering {len(processors)} processor(s) for agent `{agent_name}`')
        self._pipelines[agent_name] = processors

    def get_processors(self, agent_name: str) -> list[BaseEventProcessor]:
        """
        Get the processor pipeline for an agent.

        Args:
            agent_name: Name of the agent (ADK event author).

        Returns:
            list[BaseEventProcessor]: The agent's pipeline, or the default one.
        """
        return self._pipelines.get(agent_name, self._default_pipeline)
