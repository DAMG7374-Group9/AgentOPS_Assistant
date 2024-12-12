import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from starlette.responses import JSONResponse

from backend.schemas.transcribe import AudioTranscribeRequest
from pyannote.audio import Pipeline

from backend.config import settings
from backend.services.transcribe import upload_file_to_s3, get_whisper_model

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
async def process_audio(file: UploadFile = File(...)):
    if diarization_pipeline is None:
        return JSONResponse(
            {"error": "Diarization pipeline unavailable. Please check your Hugging Face token."},
            status_code=500,
        )

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_audio:
            audio_data = await file.read()
            temp_audio.write(audio_data)
            audio_path = temp_audio.name

        # Upload the original audio file to S3
        s3_audio_key = f"audio_files/{file.filename}"
        s3_audio_url = upload_file_to_s3(audio_path, s3_audio_key)

        whisper_model = get_whisper_model()

        # Transcribe audio using Whisper
        transcription = whisper_model.transcribe(audio_path)["segments"]

        # Perform diarization using Pyannote pipeline
        diarization = diarization_pipeline(audio_path)

        # Combine transcription and diarization
        diarized_output = []
        for segment in transcription:
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
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_txt:
            temp_txt.write(diarized_text.encode("utf-8"))
            transcription_path = temp_txt.name

        # Upload diarized transcription to S3
        s3_transcription_key = f"transcriptions/{Path(file.filename).stem}_diarized.txt"
        s3_transcription_url = upload_file_to_s3(transcription_path, s3_transcription_key)

        # Clean up temporary files
        os.remove(audio_path)
        os.remove(transcription_path)

        return {
            "transcription": diarized_text
        }

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
