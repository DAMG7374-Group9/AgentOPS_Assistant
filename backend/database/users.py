from sqlalchemy import Boolean, Column, String, Integer, DateTime, Sequence

from backend.database import Base, db_session


class UserModel(Base):
    __tablename__ = "USERS"
    __table_args__ = {'schema': 'DB_AGENTOPS_CORE.DBT_CORE_SCHEMA'}

    # id_seq = Sequence("user_id_seq", schema='DB_AGENTOPS_CORE.DBT_CORE_SCHEMA')

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    active = Column(Boolean, server_default="TRUE")
    password_timestamp = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default="CURRENT_TIMESTAMP()", nullable=False)
    modified_at = Column(DateTime, server_default="CURRENT_TIMESTAMP()", nullable=False)


def get_email_by_user_id(user_id: int) -> str:
    with db_session() as session:
        return session.query(UserModel.email).filter(UserModel.id == user_id).first()
