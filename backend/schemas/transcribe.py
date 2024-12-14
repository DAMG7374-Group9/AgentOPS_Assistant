from pydantic import BaseModel


class AudioTranscribeRequest(BaseModel):
    transcription_uuid: str
    remote_file_path: str

class AudioTranscribeResponse(BaseModel):
    personalized_summary: str
    transcription_id: int
