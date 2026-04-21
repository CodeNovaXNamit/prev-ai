"""Tests for chat memory and reminder extraction."""

from __future__ import annotations

from sqlalchemy import text

from app.chat_memory import ChatMemoryService
from app.task_manager import TaskManager


def test_chat_memory_is_encrypted_and_retrievable(session) -> None:
    memory = ChatMemoryService(session)

    stored = memory.add_message("user", "remember that my favorite topic is robotics")
    rows = session.execute(text("SELECT content_encrypted, is_system_log FROM chat_messages WHERE id = :id"), {"id": stored["id"]}).one()

    assert "favorite topic" not in rows.content_encrypted
    assert rows.is_system_log == 0
    recent = memory.list_recent_messages()
    assert recent[-1]["content"] == "remember that my favorite topic is robotics"


def test_chat_memory_flags_noisy_logs_and_hides_them_from_recent_history(session) -> None:
    memory = ChatMemoryService(session)

    stored = memory.add_message(
        "user",
        "pytest -q\nTraceback (most recent call last):\nPermission denied\nrm -rf build\nlsof -i :8000",
    )

    rows = session.execute(text("SELECT is_system_log FROM chat_messages WHERE id = :id"), {"id": stored["id"]}).one()

    assert rows.is_system_log == 1
    assert memory.list_recent_messages() == []


def test_task_extraction_supports_remind_me_phrasing(session) -> None:
    manager = TaskManager(session)

    created = manager.create_tasks_from_message("remind me to call the advisor tomorrow")

    assert created[0]["title"] == "call the advisor tomorrow"
