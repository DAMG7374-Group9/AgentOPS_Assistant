from fastapi import APIRouter, Depends

from backend.schemas.chat import QueryRequest, QueryResponse, ChatHistoryResponse
from backend.services.auth_bearer import get_current_user_id
from backend.services.chat import process_llm_query, get_chat_history

chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post(
    "/query",
)
async def process_query(request: QueryRequest, user_id: int = Depends(get_current_user_id)) -> QueryResponse:
    """
    Process a Q/A query
    """
    return await process_llm_query(
        prompt=request.prompt, transcription_id=request.transcription_id, model_choice=request.model,
        chat_session_id=request.chat_session_id, user_id=user_id
    )


@chat_router.get(
    "/history"
)
async def get_chat_history_view(chat_session_id: int, user_id: int = Depends(get_current_user_id)) -> ChatHistoryResponse:
    return await get_chat_history(chat_session_id=chat_session_id)
