"""SQLAlchemy ORM models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(tz=timezone.utc)


class TimestampMixin:
    """Shared timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class TaskRecord(TimestampMixin, Base):
    """Encrypted task row."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title_encrypted: Mapped[str] = mapped_column(Text())
    description_encrypted: Mapped[str] = mapped_column(Text(), default="")
    due_date: Mapped[str | None] = mapped_column(String(64), nullable=True)
    priority: Mapped[str] = mapped_column(String(16), default="medium")
    completed: Mapped[bool] = mapped_column(Boolean, default=False)


class EventRecord(TimestampMixin, Base):
    """Encrypted event row."""

    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title_encrypted: Mapped[str] = mapped_column(Text())
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    location_encrypted: Mapped[str] = mapped_column(Text(), default="")
    notes_encrypted: Mapped[str] = mapped_column(Text(), default="")


class NoteRecord(TimestampMixin, Base):
    """Encrypted note row."""

    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title_encrypted: Mapped[str] = mapped_column(Text())
    note_text_encrypted: Mapped[str] = mapped_column(Text())
    summary_encrypted: Mapped[str | None] = mapped_column(Text(), nullable=True)


class ChatMessageRecord(TimestampMixin, Base):
    """Encrypted chat history row."""

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    role: Mapped[str] = mapped_column(String(16))
    content_encrypted: Mapped[str] = mapped_column(Text())


class UserMemoryRecord(TimestampMixin, Base):
    """Encrypted remembered user fact."""

    __tablename__ = "user_memories"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    key: Mapped[str] = mapped_column(String(64), index=True)
    value_encrypted: Mapped[str] = mapped_column(Text())


class BehaviorEvent(TimestampMixin, Base):
    """Tracked interaction used for adapting the UI and analytics."""

    __tablename__ = "behavior_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feature: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(64))
    detail_encrypted: Mapped[str | None] = mapped_column(Text(), nullable=True)
