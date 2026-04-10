from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import DeclarativeBase, Session

from . import config as _config_paths


class Base(DeclarativeBase):
    pass


class Config(Base):
    __tablename__ = "config"
    key = Column(String, primary_key=True)
    value = Column(String)


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _config_paths.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(f"sqlite:///{_config_paths.DB_PATH}")
    return _engine


def get_session():
    return Session(get_engine())
