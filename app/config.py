"""Application configuration for the privacy-first assistant."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _normalize_database_url(raw_url: str) -> str:
    """Expand relative SQLite paths into absolute SQLAlchemy URLs."""
    if raw_url.startswith("sqlite:///") and ":memory:" not in raw_url:
        relative = raw_url.removeprefix("sqlite:///")
        if not Path(relative).is_absolute():
            resolved = (BASE_DIR / relative).resolve()
            resolved.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{resolved.as_posix()}"
    return raw_url


def _parse_cors_origins(value: str) -> list[str]:
    """Parse a comma-separated CORS origins string."""
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@dataclass(frozen=True)
class AppSettings:
    """Runtime configuration loaded from environment variables."""

    app_name: str
    model_name: str
    ollama_url: str
    encryption_key: str
    database_url: str
    request_timeout: int
    allow_external_network: bool
    cors_origins: list[str]


class HealthStatus(BaseModel):
    """Simple application status model."""

    app_name: str
    offline_mode: bool
    ollama_available: bool
    database_url: str
    active_model: str


class ChatRequest(BaseModel):
    """Request payload for chat."""

    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    """Assistant response payload."""

    response: str
    source: str
    created_tasks: list[dict[str, str]]


class TaskBase(BaseModel):
    """Common task fields."""

    title: str = Field(..., min_length=1)
    description: str = ""
    due_date: str | None = None
    priority: str = "medium"
    completed: bool = False


class TaskUpdate(BaseModel):
    """Task update fields."""

    title: str | None = None
    description: str | None = None
    due_date: str | None = None
    priority: str | None = None
    completed: bool | None = None


class EventBase(BaseModel):
    """Common event fields."""

    title: str = Field(..., min_length=1)
    start_time: str
    end_time: str
    location: str = ""
    notes: str = ""


class EventUpdate(BaseModel):
    """Event update fields."""

    title: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    location: str | None = None
    notes: str | None = None


class NoteCreate(BaseModel):
    """Note creation payload."""

    title: str = Field(..., min_length=1)
    note_text: str = Field(..., min_length=1)


class SummaryRequest(BaseModel):
    """Notes summarization payload."""

    title: str = ""
    note_text: str = Field(..., min_length=1)


class AnalyticsResponse(BaseModel):
    """Analytics dashboard payload."""

    sessions: int
    tasks_completed_percent: int
    saved_notes: int
    scheduled_events: int
    weekly_activity: list[int]
    completion_series: list[int]
    timeline: list[dict[str, str]]
    preferred_feature: str


class SystemCheckResult(BaseModel):
    """Single dashboard check result."""

    name: str
    status: str
    detail: str


class SystemStatusResponse(BaseModel):
    """Expanded system dashboard payload."""

    health: HealthStatus
    database_connected: bool
    total_tasks: int
    total_summaries: int
    total_events: int
    checks: list[SystemCheckResult]
    latest_test_results: list[SystemCheckResult]


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached application settings."""
    return AppSettings(
        app_name=os.getenv("APP_NAME", "Privacy AI Assistant"),
        model_name=os.getenv("MODEL_NAME", "phi3"),
        ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        encryption_key=os.getenv("ENCRYPTION_KEY", "local-dev-key"),
        database_url=_normalize_database_url(
            os.getenv("DATABASE_URL", "sqlite:///data/assistant.db")
        ),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
        allow_external_network=os.getenv("ALLOW_EXTERNAL_NETWORK", "false").lower() == "true",
        cors_origins=_parse_cors_origins(
            os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        ),
    )
