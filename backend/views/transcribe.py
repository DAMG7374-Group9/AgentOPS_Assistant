from fastapi import APIRouter

from backend.schemas.transcribe import AudioTranscribeRequest
from backend.services.transcribe import transcribe_audio

transcribe_router = APIRouter(prefix="/transcribe", tags=["transcribe"])


@transcribe_router.post(
    "/audio",
)
async def transcribe(
    request: AudioTranscribeRequest,
        # user_id: int = Depends(get_current_user_id)
):
    """
    Transcribes audio to text and returns the result
    """
    return await transcribe_audio(request.remote_file_path)
