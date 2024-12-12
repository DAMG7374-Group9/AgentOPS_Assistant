"""async def transcribe_audio(remote_file_path: str) -> str:

    # TODO: Add transcription record and return ID
    ..."""
from functools import lru_cache

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile
from pathlib import Path
import whisper
import boto3
import os
from dotenv import load_dotenv

from backend.config import settings

# Fetch sensitive data from environment variables
HF_TOKEN = os.getenv("HF_TOKEN", "default_hf_token")


# Set up FFmpeg path (if needed for your environment)
FFMPEG_PATH = r"C:\ffmeg\ffmpeg-7.0.2-essentials_build\bin\ffmpeg.exe"
os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_PATH)

# Load Whisper model for transcription
@lru_cache(maxsize=1)
def get_whisper_model():
    return whisper.load_model("base")

# # Initialize Pyannote pipeline for diarization
# try:
#     diarization_pipeline = Pipeline.from_pretrained(
#         "pyannote/speaker-diarization-3.1",
#         use_auth_token=HF_TOKEN
#     )
#     print("Diarization pipeline loaded successfully.")
# except Exception as e:
#     diarization_pipeline = None
#     print(f"Failed to load diarization pipeline: {e}")

# Function to upload files to S3
def upload_file_to_s3(file_path, s3_key):
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        s3_client.upload_file(file_path, settings.AWS_S3_BUCKET, s3_key)
        return ""
    except Exception as e:
        raise Exception(f"Failed to upload file to S3: {e}")
