"""Tests for encrypted ORM persistence."""

from __future__ import annotations

from sqlalchemy import text

from app.scheduler import SchedulerManager
from app.task_manager import TaskManager


def test_database_stores_encrypted_task_fields(session) -> None:
    manager = TaskManager(session)

    record = manager.add_task(title="Write report", description="Keep it private")
    row = session.execute(
        text("SELECT title_encrypted, description_encrypted FROM tasks WHERE id = :id"),
        {"id": record["id"]},
    ).one()

    assert "Write report" not in row.title_encrypted
    assert "Keep it private" not in row.description_encrypted


def test_database_delete_record(session) -> None:
    scheduler = SchedulerManager(session)
    event = scheduler.add_event(
        title="Meeting",
        start_time="2026-04-17T09:00:00",
        end_time="2026-04-17T09:30:00",
        location="War room",
    )

    deleted = scheduler.delete_event(event["id"])

    assert deleted is True
    assert scheduler.list_events() == []
