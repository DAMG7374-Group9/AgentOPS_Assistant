from fastapi import APIRouter

from backend.views.auth import auth_router
from backend.views.chat import chat_router
from backend.views.transcribe import transcribe_router
from backend.views.users import users_router

central_router = APIRouter()

central_router.include_router(auth_router)
central_router.include_router(chat_router)
central_router.include_router(users_router)
central_router.include_router(transcribe_router)
