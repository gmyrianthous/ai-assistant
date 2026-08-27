from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

_STATIC_DIR = Path(__file__).parent.parent / 'static'


@router.get('/chat', include_in_schema=False)
async def chat_ui() -> FileResponse:
    """
    Serve the minimal AG-UI chat client for local development.

    Returns:
        FileResponse: The static chat page.
    """
    return FileResponse(_STATIC_DIR / 'chat.html', media_type='text/html')
