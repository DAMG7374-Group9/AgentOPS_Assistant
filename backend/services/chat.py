
from backend.agent import agent_workflow
from backend.database.chat_sessions import create_chat_session, update_last_message_time
from backend.database.messages import get_messages_by_chat_id
from backend.schemas.chat import QueryResponse, ChatHistoryResponse


async def process_llm_query(
    prompt: str, transcription_id: int, model_choice: str, chat_session_id: int | None, user_id: int
) -> QueryResponse:
    """Process a Q/A query and store the result"""

    if not chat_session_id:
        chat_session = create_chat_session(user_id=user_id, transcription_id=transcription_id)
        chat_session_id = chat_session.id

    response = agent_workflow.invoke({"prompt": prompt, "chat_session_id": chat_session_id})

    print(response["steps"])

    tools_used = ["vector_search"]
    if response.get("perform_web_search", False):
        tools_used.append("web_search")

    update_last_message_time(chat_session_id)
    return QueryResponse(response=response, chat_session_id=chat_session_id, references=[], tools_used=tools_used)


async def get_chat_history(chat_session_id: int) -> ChatHistoryResponse:
    messages = get_messages_by_chat_id(chat_session_id)
    return ChatHistoryResponse(history=[QueryResponse(
        response=msg.content, chat_session_id=msg.chat_session_id, references=msg.references, tools_used=msg
    ) for msg in messages])
