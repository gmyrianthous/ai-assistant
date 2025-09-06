from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

from ai_assistant.api.routes import health
from ai_assistant.api.routes import session
from ai_assistant.exceptions import AppException
from ai_assistant.exceptions import AuthorizationException
from ai_assistant.exceptions import NotFoundException

app = FastAPI()

app.include_router(health.router)
app.include_router(session.router)


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
