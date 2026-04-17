"""SQLAlchemy engine and session management."""

from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for ORM models."""


def _engine_kwargs(database_url: str) -> dict[str, object]:
    kwargs: dict[str, object] = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


@lru_cache(maxsize=1)
def get_engine():
    """Return the shared SQLAlchemy engine."""
    settings = get_settings()
    return create_engine(settings.database_url, **_engine_kwargs(settings.database_url))


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Return the configured session factory."""
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Yield a managed database session for FastAPI dependencies."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def init_database() -> None:
    """Create database tables for local development."""
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
