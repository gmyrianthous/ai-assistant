import logging
from typing import Annotated

from fastapi import Depends
from fastapi import Request

from ai_assistant.services.ai.adk.session_factory import ADKSessionService
from ai_assistant.services.ai.service import AIService

logger = logging.getLogger(__name__)


def get_session_service(request: Request) -> ADKSessionService:
    """
    Get the singleton ADK session service instance from app state.

    This session service is initialized once during application startup
    and shared across all requests for performance and consistency.

    Args:
        request: The FastAPI request object.

    Returns:
        ADKSessionService: The singleton session service instance.
    """
    return request.app.state.session_service


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
