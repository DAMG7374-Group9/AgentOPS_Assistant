from pydantic import BaseModel


class AudioTranscribeRequest(BaseModel):
    transcription_uuid: str
    remote_file_path: str
