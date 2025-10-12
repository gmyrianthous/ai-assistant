import logging

from google.adk.sessions import DatabaseSessionService
from google.adk.sessions import InMemorySessionService
from google.adk.sessions import VertexAiSessionService

from ai_assistant.common.settings import settings

logger = logging.getLogger(__name__)

ADKSessionService = InMemorySessionService | VertexAiSessionService | DatabaseSessionService


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
