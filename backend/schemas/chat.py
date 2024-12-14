from pydantic import BaseModel


class QueryRequest(BaseModel):
    prompt: str
    model: str
    transcription_id: int
    chat_session_id: int | None
    transcript: str | None


class QueryResponse(BaseModel):
    chat_session_id: int
    response: str
    references: list[str]
    tools_used: list[str]

class ChatHistoryResponse(BaseModel):
    history: list[QueryResponse]
