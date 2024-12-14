import os
import tempfile
from idlelib.pyparse import trans
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends
from starlette.responses import JSONResponse

from backend.database.transcriptions import create_transcription_record, update_transcription_text, \
    get_transcription_by_id
from backend.schemas.transcribe import AudioTranscribeRequest, AudioTranscribeResponse
from pyannote.audio import Pipeline

from backend.config import settings
from backend.services.auth_bearer import get_current_user_id
from backend.services.transcribe import upload_file_to_s3, get_whisper_model, generate_personalized_summary
from backend.utils import write_audio_to_file, write_transcription_to_file

transcribe_router = APIRouter(prefix="/transcribe", tags=["transcribe"])


# @transcribe_router.post(
#     "/audio",
# )
# async def transcribe(
#     request: AudioTranscribeRequest,
#         # user_id: int = Depends(get_current_user_id)
# ):
#     """
#     Transcribes audio to text and returns the result
#     """
#     return await transcribe_audio(request.remote_file_path)


# Initialize Pyannote pipeline for diarization
try:
    diarization_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=settings.HF_TOKEN
    )
    print("Diarization pipeline loaded successfully.")
except Exception as e:
    diarization_pipeline = None
    print(f"Failed to load diarization pipeline: {e}")

@transcribe_router.post("/upload-audio/")
async def process_audio(file: UploadFile = File(...), user_id: int = Depends(get_current_user_id)):
    if diarization_pipeline is None:
        return JSONResponse(
            {"error": "Diarization pipeline unavailable. Please check your Hugging Face token."},
            status_code=500,
        )
    transcription_record = create_transcription_record(user_id=user_id)

    audio_file_path = await write_audio_to_file(file, str(transcription_record.id))
    whisper_model = get_whisper_model()

    # Transcribe audio using Whisper
    transcription_output = whisper_model.transcribe(audio_file_path)["segments"]

    # Perform diarization using Pyannote pipeline
    diarization = diarization_pipeline(audio_file_path)

    # Combine transcription and diarization
    diarized_output = []
    for segment in transcription_output:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]
        speaker = "Unknown"
        for turn, _, speaker_id in diarization.itertracks(yield_label=True):
            if turn.start <= start_time <= turn.end:
                speaker = f"{speaker_id}"
        diarized_output.append(f"[{start_time:.2f} - {end_time:.2f}] {speaker}: {text}")

    # Save diarized transcription to a file
    diarized_text = "\n".join(diarized_output)
    diarized_file_path = await write_transcription_to_file(diarized_text, str(transcription_record.id))
    personalized_summary = generate_personalized_summary(transcription_path=diarized_file_path, user_id=user_id)

    update_transcription_text(transcription_id=transcription_record.id, transcription_text=diarized_text, personalized_summary=personalized_summary)

    return AudioTranscribeResponse(
        personalized_summary=personalized_summary, transcription_id=transcription_record.id
    )
