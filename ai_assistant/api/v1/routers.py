from ag_ui_adk import add_adk_fastapi_endpoint
from fastapi import APIRouter

from ai_assistant.api.v1.routes import session
from ai_assistant.services.ai.agui import create_agui_agent

V1_API_PREFIX = '/api/v1'

v1_api_router = APIRouter()

# Include all the v1 routers here
v1_api_router.include_router(session.router, prefix='/chatbot', tags=['session'])

# Chat endpoint speaking the AG-UI protocol (POST /api/v1/chat)
add_adk_fastapi_endpoint(v1_api_router, create_agui_agent(), path='/chat')
