import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from backend.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
    __mapper_args__ = {"eager_defaults": True}


class DatabaseSession:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.info("Created new database session object")
            cls._instance = super().__new__(cls)
            cls._instance.db_engine = create_engine(settings.POSTGRES_URI)
            cls._instance.session_maker = scoped_session(
                sessionmaker(autocommit=False, autoflush=True, bind=cls._instance.db_engine)
            )
        return cls._instance

    @classmethod
    def db_session(cls):
        return cls().session_maker()


@contextmanager
def db_session() -> Session:
    _session = DatabaseSession.db_session()
    try:
        yield _session
    except Exception as e:
        raise ValueError(f"Failed to connect to database: {e}")
    finally:
        _session.close()