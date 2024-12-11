from sqlalchemy import Boolean, Column, String, Integer, DateTime, Sequence

from backend.database import Base


class UserModel(Base):
    __tablename__ = "users"
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
