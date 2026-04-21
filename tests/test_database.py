"""Tests for encrypted ORM persistence."""

from __future__ import annotations

from datetime import datetime

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


def test_task_add_deduplicates_and_reopens_existing_completed_task(session) -> None:
    manager = TaskManager(session)

    first = manager.add_task(title="Homework", description="Old", completed=True)
    second = manager.add_task(title="Homework", description="Fresh", completed=False)

    assert first["id"] == second["id"]
    assert second["completed"] is False
    assert second["description"] == "Fresh"
    assert len(manager.list_tasks()) == 1


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


def test_scheduler_extracts_meeting_from_chat_message(session) -> None:
    scheduler = SchedulerManager(session)

    created = scheduler.create_events_from_message(
        "I have a meeting on 20th april at 9am in chandigarh",
        now=datetime(2026, 4, 18, 12, 0, 0),
    )

    assert created[0]["title"] == "Meeting"
    assert created[0]["start_time"].startswith("2026-04-20T09:00:00")
    assert created[0]["end_time"].startswith("2026-04-20T10:00:00")
    assert created[0]["location"] == "Chandigarh"


def test_scheduler_extracts_location_from_at_location_phrase(session) -> None:
    scheduler = SchedulerManager(session)

    created = scheduler.create_events_from_message(
        "i have a meeting on 20th april at 9 am at location ludhiana",
        now=datetime(2026, 4, 18, 12, 0, 0),
    )

    assert created[0]["title"] == "Meeting"
    assert created[0]["start_time"].startswith("2026-04-20T09:00:00")
    assert created[0]["location"] == "Ludhiana"
