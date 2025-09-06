from fastapi import APIRouter

router = APIRouter()


@router.get('/health')
async def health() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        dict[str, str]: A dictionary with the status of the application.
    """
    return {'status': 'OK'}
