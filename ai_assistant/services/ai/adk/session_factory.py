import logging

from google.adk.sessions import DatabaseSessionService
from google.adk.sessions import InMemorySessionService
from google.adk.sessions import VertexAiSessionService

from ai_assistant.common.settings import settings

logger = logging.getLogger(__name__)

ADKSessionService = InMemorySessionService | VertexAiSessionService | DatabaseSessionService


_session_service: ADKSessionService | None = None


def create_session_service() -> ADKSessionService:
    """
    Create an ADK session service based on the application environment.

    Returns:
        ADKSessionService: The configured session service instance.

    Raises:
        ValueError: If ENVIRONMENT is not recognized.
    """
    environment = settings.ENVIRONMENT.lower()
    logger.info(f'Initialising Session Service for environment `{environment}`')

    if environment in ['staging', 'production']:
        logger.info(
            f'Using VertexAiSessionService for GCP project `{settings.GOOGLE_CLOUD_PROJECT}` '
            f'and location `{settings.GOOGLE_CLOUD_LOCATION}`.'
        )
        return VertexAiSessionService(
            project_id=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_LOCATION,
        )

    logger.info('Using InMemorySessionService for development')
    return InMemorySessionService()


def get_session_service() -> ADKSessionService:
    """
    Get the singleton ADK session service instance.

    This function returns the module-level singleton that is initialized
    once during application startup. All requests share the same instance.

    Returns:
        ADKSessionService: The singleton session service instance.

    Raises:
        RuntimeError: If the session service has not been initialized.
    """
    global _session_service
    if _session_service is None:
        raise RuntimeError(
            'Session service has not been initialized. '
            'Call initialize_session_service() during app startup.'
        )
    return _session_service


def initialize_session_service() -> None:
    """
    Initialize the singleton session service instance.
    This should be called once during application startup.
    """
    global _session_service
    if _session_service is None:
        _session_service = create_session_service()
        logger.info(f'Initialized singleton session service: {type(_session_service).__name__}')
    else:
        logger.warning('Session service already initialized')
