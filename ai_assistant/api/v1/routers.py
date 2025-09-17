from fastapi import APIRouter

from ai_assistant.api.v1.routes import chatbot
from ai_assistant.api.v1.routes import session

V1_API_PREFIX = '/api/v1'

v1_api_router = APIRouter()

# Include all the v1 routers here
v1_api_router.include_router(session.router, prefix='/chatbot', tags=['session', 'chatbot'])
v1_api_router.include_router(chatbot.router, prefix='/chatbot', tags=['chat', 'chatbot'])
