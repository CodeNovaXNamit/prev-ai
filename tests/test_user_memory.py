"""Tests for encrypted remembered facts."""

from __future__ import annotations

from sqlalchemy import text

from app.memory_service import UserMemoryService


def test_user_memory_is_encrypted_and_recallable(session) -> None:
    service = UserMemoryService(session)

    saved = service.upsert_memory("name", "Namit")
    row = session.execute(
        text("SELECT value_encrypted FROM user_memories WHERE key = :key"),
        {"key": "name"},
    ).one()

    assert "Namit" not in row.value_encrypted
    assert saved["value"] == "Namit"
    assert service.get_memory("name")["value"] == "Namit"


def test_capture_memories_without_explicit_remember_phrase(session) -> None:
    service = UserMemoryService(session)

    captured = service.capture_memories_from_message(
        "My name is Namit and I live in Chandigarh and my favorite language is python"
    )

    keys = {item["key"] for item in captured}
    assert {"name", "location", "favorite_language"} <= keys
    assert service.get_memory("location")["value"] == "Chandigarh"
    assert service.get_memory("favorite_language")["value"] == "Python"
