from sqlalchemy import Column, Integer, Sequence, Text, DateTime

from backend.database import Base, db_session


class TranscriptionModel(Base):
    __tablename__ = 'Transcriptions'
    __table_args__ = {'schema': 'DB_AGENTOPS_CORE.DBT_CORE_SCHEMA'}

    # transcription_id_seq = Sequence("transcription_id_seq", schema='DB_AGENTOPS_CORE.DBT_CORE_SCHEMA')

    id = Column(Integer, Sequence("transcriptions_id_seq"), primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    transcription_text = Column(Text, nullable=False)
    personalized_summary = Column(Text, nullable=True)
    created_at =  Column(DateTime, server_default="CURRENT_TIMESTAMP()", nullable=False)


def create_transcription_record() -> TranscriptionModel:
    ...


def get_transcription_by_id(transcription_id: int) -> TranscriptionModel:
    with db_session() as session:
        return session.query(TranscriptionModel).filter(TranscriptionModel.id == transcription_id).first()
