from fastapi import APIRouter

from backend.schemas.chat import QueryRequest
from backend.services.chat import process_llm_query

chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post(
    "/query",
)
async def process_query(
        request: QueryRequest,
        # user_id: int = Depends(get_current_user_id)
):
    """
    Process a Q/A query
    """
    return await process_llm_query(
            "1", request.prompt, request.model, 1
        )
