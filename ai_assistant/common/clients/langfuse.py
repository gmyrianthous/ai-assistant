import logging

from langfuse import Langfuse

from ai_assistant.common.settings import settings

logger = logging.getLogger(__name__)


class LangfuseClientSingleton:
    _client: Langfuse | None = None

    @classmethod
    def get_langfuse_client(cls) -> Langfuse | None:
        if cls._client is None:
            logger.info('Initializing Langfuse client')
            try:
                cls._client = Langfuse(
                    host=settings.LANGFUSE_HOST,
                    secret_key=settings.LANGFUSE_SECRET_KEY.get_secret_value(),
                    public_key=settings.LANGFUSE_PUBLIC_KEY.get_secret_value(),
                    environment=settings.ENVIRONMENT,
                )
                logger.info('Langfuse client initialized successfully')
            except Exception as e:
                logger.error(f'Error initializing Langfuse client: {str(e)}')
                raise

        return cls._client
