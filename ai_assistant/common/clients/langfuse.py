"""
Langfuse client for prompt management and observability.

Provides lazy initialization with authentication verification.
"""
import logging

from langfuse import Langfuse

from ai_assistant.common.settings import settings

logger = logging.getLogger(__name__)

_langfuse_client: Langfuse | None = None


def get_langfuse_client() -> Langfuse:
    """
    Get the Langfuse client, initializing it lazily on first access.

    The client is cached after first initialization and reused across calls.

    Returns:
        Langfuse: The authenticated Langfuse client instance

    Raises:
        Exception: If Langfuse initialization or authentication fails
    """
    global _langfuse_client

    if _langfuse_client is None:
        logger.info('Initializing Langfuse client')

        try:
            _langfuse_client = Langfuse(
                host=settings.LANGFUSE_HOST,
                secret_key=settings.LANGFUSE_SECRET_KEY.get_secret_value(),
                public_key=settings.LANGFUSE_PUBLIC_KEY.get_secret_value(),
                environment=settings.ENVIRONMENT,
            )
            logger.info('Langfuse client initialized successfully')

            # Verify authentication
            if _langfuse_client.auth_check():
                logger.info('Langfuse client is authenticated and ready!')
            else:
                error_msg = 'Langfuse authentication failed. Please check your credentials and host.'
                logger.error(error_msg)
                _langfuse_client = None
                raise RuntimeError(error_msg)

        except Exception as e:
            logger.error(f'Error initializing Langfuse client: {e}')
            _langfuse_client = None
            raise

    return _langfuse_client
