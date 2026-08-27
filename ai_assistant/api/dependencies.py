"""FastAPI dependency injection configuration."""

import logging

from ai_assistant.services.ai.adk.session_factory import ADKSessionService
from ai_assistant.services.ai.adk.session_factory import (
    get_session_service as _get_session_service,
)

logger = logging.getLogger(__name__)


def get_session_service() -> ADKSessionService:
    """
    Get the singleton ADK session service instance.

    Returns:
        ADKSessionService: The singleton session service instance.
    """
    return _get_session_service()
