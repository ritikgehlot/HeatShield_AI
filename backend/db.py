"""Database engine/session setup.

SQLite (demo/local default) uses ``Base.metadata.create_all`` for zero-friction
startup. PostgreSQL is expected to be migrated with Alembic
(``alembic upgrade head``) — see /alembic. Both paths share the same models;
geometry is stored as portable GeoJSON text rather than a PostGIS-specific
column type, so behavior is identical on both backends (see
docs/ARCHITECTURE_V2.md for the tradeoffs and the native-PostGIS upgrade path).
"""
from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from . import models  # noqa: F401 - register model metadata

    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency — shared by main.py and every router."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
