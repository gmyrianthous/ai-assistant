import logging
import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

from ai_assistant.api.routes.health import router as health_router
from ai_assistant.api.v1.routers import V1_API_PREFIX
from ai_assistant.api.v1.routers import v1_api_router
from ai_assistant.common.clients.langfuse import get_langfuse_client
from ai_assistant.common.settings import settings
from ai_assistant.exceptions import AppException
from ai_assistant.exceptions import AuthorizationException
from ai_assistant.exceptions import NotFoundException
from ai_assistant.services.ai.adk.session_factory import create_session_service

logging.config.fileConfig(
    Path(__file__).parent / '../../logging.conf', disable_existing_loggers=False
)

logging.getLogger().setLevel(settings.LOGGING_LEVEL)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handle application startup and shutdown.

    Args:
        app (FastAPI): The FastAPI application.

    Yields:
        None: The application is running.
    """
    logger.info('Starting application initialisation...')

    # Initialise session service
    logger.info('Starting session service initialisation...')
    session_service = create_session_service()
    app.state.session_service = session_service
    logger.info(f'Initialised session service: {type(session_service).__name__}')

    # Initialise langfuse client
    logger.info('Starting langfuse client initialisation...')
    langfuse = get_langfuse_client()
    langfuse.flush()
    logger.info('Initialised langfuse client')

    logger.info('Application startup complete')

    yield

    logger.info('Application shutdown complete')


app = FastAPI(title='AI Assistant', lifespan=lifespan)

# Health endpoint at root level
# k8s expects a health endpoint at the root level
app.include_router(health_router)

# Versioned API endpoints
app.include_router(v1_api_router, prefix=V1_API_PREFIX)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    match exc:
        case NotFoundException():
            status_code = status.HTTP_404_NOT_FOUND
        case AuthorizationException():
            status_code = status.HTTP_401_UNAUTHORIZED
        case _:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse({'detail': str(exc)}, status_code=status_code)
