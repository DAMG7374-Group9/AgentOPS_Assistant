from idlelib.pyparse import trans

from sqlalchemy import Column, Integer, Sequence, DateTime, text, VARCHAR, String

from backend.database import Base, db_session


class TranscriptionModel(Base):
    __tablename__ = 'TRANSCRIPTIONS'
    __table_args__ = {'schema': 'DB_AGENTOPS_CORE.DBT_CORE_SCHEMA'}

    id = Column(Integer, Sequence("transcriptions_id_seq"), primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    transcription_text = Column(String(16777216), nullable=False)
    personalized_summary = Column(String(16777216), nullable=True)
    created_at =  Column(DateTime, server_default="CURRENT_TIMESTAMP()", nullable=False)


def create_transcription_record(user_id: int) -> TranscriptionModel:
    with db_session() as session:
        new_transcription = TranscriptionModel(user_id=user_id)
        session.add(new_transcription)
        session.commit()
        session.refresh(new_transcription)
        return new_transcription


def get_transcription_by_id(transcription_id: int) -> TranscriptionModel:
    with db_session() as session:
        return session.query(TranscriptionModel).filter(TranscriptionModel.id == transcription_id).first()


def update_transcription_text(transcription_id: int, transcription_text: str, personalized_summary: str):
    with db_session() as session:
        session.query(TranscriptionModel).filter(TranscriptionModel.id == transcription_id).update({
            "transcription_text": transcription_text, "personalized_summary": personalized_summary
        })
        session.commit()
