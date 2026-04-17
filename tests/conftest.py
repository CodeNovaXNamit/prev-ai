"""Shared pytest fixtures for backend tests."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture()
def session(tmp_path, monkeypatch) -> Generator[Session, None, None]:
    """Provide an isolated SQLAlchemy session bound to a temp SQLite database."""
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("ENCRYPTION_KEY", "test-suite-key")
    monkeypatch.setenv("ALLOW_EXTERNAL_NETWORK", "false")

    from app.config import get_settings
    from app.database import Base, get_engine, get_session_factory
    from app import models  # noqa: F401

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        get_session_factory.cache_clear()
        get_engine.cache_clear()
        get_settings.cache_clear()


@pytest.fixture()
def client(session: Session) -> Generator[TestClient, None, None]:
    """Provide a FastAPI test client backed by the fixture session."""
    from app.main import app, get_db

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
