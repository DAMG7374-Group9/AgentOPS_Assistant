from sqlalchemy import Column, Integer, Sequence, DateTime, String, func

from backend.database import Base, db_session


class ChatSessionModel(Base):
    __tablename__ = 'chat_session'
    __table_args__ = {'schema': 'DB_AGENTOPS_CORE.DBT_CORE_SCHEMA'}

    # chat_id_seq = Sequence("chat_session_id_seq", schema='DB_AGENTOPS_CORE.DBT_CORE_SCHEMA')

    id = Column(Integer, Sequence("chat_session_id_seq"), primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=True)
    transcription_id = Column(Integer, nullable=False)
    created_at =  Column(DateTime, server_default="CURRENT_TIMESTAMP()", nullable=False)
    last_message_time =  Column(DateTime, server_default="CURRENT_TIMESTAMP()", nullable=False)


def create_chat_session(user_id: int, transcription_id: int) -> ChatSessionModel:
    with db_session() as session:
        _chat_session = ChatSessionModel(user_id=user_id, title='Untitled', transcription_id=transcription_id)
        session.add(_chat_session)
        session.commit()

        session.refresh(_chat_session)
        return _chat_session


def fetch_chat_session_by_id(chat_session_id: int) -> ChatSessionModel:
    with db_session() as session:
        return session.query(ChatSessionModel).filter(ChatSessionModel.id == chat_session_id).first()


def update_last_message_time(chat_session_id: int) -> ChatSessionModel:
    chat_session = fetch_chat_session_by_id(chat_session_id)

    with db_session() as session:
        chat_session.last_message_time = func.now()

        session.add(chat_session)
        session.commit()
        session.refresh(chat_session)
        return chat_session
