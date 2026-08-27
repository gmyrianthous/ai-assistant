"""
AG-UI integration for the ADK orchestrator agent.

Exposes the orchestrator through the AG-UI protocol (https://docs.ag-ui.com)
using the official ADK middleware. The middleware translates ADK events into
the standard AG-UI event stream (RUN_STARTED, TEXT_MESSAGE_*, TOOL_CALL_*,
RUN_FINISHED, ...) consumed by AG-UI clients such as CopilotKit.
"""

import logging
from collections.abc import AsyncGenerator

from ag_ui.core import BaseEvent
from ag_ui.core import RunAgentInput
from ag_ui_adk import ADKAgent
from langfuse import propagate_attributes

from ai_assistant.common.settings import settings
from ai_assistant.services.ai.adk.agents.orchestrator.agent import orchestrator_agent
from ai_assistant.services.ai.adk.session_factory import get_session_service
from ai_assistant.services.ai.adk.session_factory import initialize_session_service

logger = logging.getLogger(__name__)


def _extract_user_id(input: RunAgentInput) -> str:
    """
    Extract the user ID from an AG-UI run input.

    Clients pass the user ID via `forwardedProps.user_id`.

    Args:
        input: The AG-UI run input.

    Returns:
        str: The user ID, or 'anonymous' if none was provided.
    """
    props = input.forwarded_props
    if isinstance(props, dict) and props.get('user_id'):
        return str(props['user_id'])
    return 'anonymous'


class TracedADKAgent(ADKAgent):
    """ADKAgent that correlates Langfuse traces with the AG-UI user and thread."""

    async def run(self, input: RunAgentInput) -> AsyncGenerator[BaseEvent, None]:
        with propagate_attributes(
            user_id=_extract_user_id(input),
            session_id=input.thread_id,
        ):
            async for event in super().run(input):
                yield event


def create_agui_agent() -> ADKAgent:
    """
    Create the AG-UI agent wrapping the ADK orchestrator.

    Uses the application's session service singleton so conversations started
    over AG-UI are visible through the session REST endpoints (the AG-UI
    threadId is used directly as the ADK session id).

    Returns:
        ADKAgent: The configured AG-UI middleware agent.
    """
    initialize_session_service()
    logger.info('Creating AG-UI agent for orchestrator')
    return TracedADKAgent(
        adk_agent=orchestrator_agent,
        app_name=settings.APP_NAME,
        session_service=get_session_service(),
        user_id_extractor=_extract_user_id,
        use_thread_id_as_session_id=True,
    )
