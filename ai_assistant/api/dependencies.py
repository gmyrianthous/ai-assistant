import logging
from typing import Annotated

from fastapi import Depends

from ai_assistant.services.ai.adk.session_factory import ADKSessionService
from ai_assistant.services.ai.adk.session_factory import (
    get_session_service as _get_session_service,
)
from ai_assistant.services.ai.service import AIService

logger = logging.getLogger(__name__)


def get_session_service() -> ADKSessionService:
    """
    Get the singleton ADK session service instance.

    This session service is initialized once during application startup
    and shared across all requests for performance and consistency.

    Returns:
        ADKSessionService: The singleton session service instance.
    """
    return _get_session_service()


def get_ai_service(
    session_service: Annotated[ADKSessionService, Depends(get_session_service)],
) -> AIService:
    """
    FastAPI dependency to get an AI service.

    Args:
        session_service: The injected ADK session service.

    Returns:
        AIService: The configured AI service instance.
    """
    logger.debug('Creating AI service')
    return AIService(session_service=session_service)
