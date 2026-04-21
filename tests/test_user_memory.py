"""Tests for encrypted remembered facts."""

from __future__ import annotations

from sqlalchemy import text
from unittest.mock import Mock, patch

from app.memory_service import UserMemoryService
from app.semantic_memory import SemanticMemoryService


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
    assert saved["importance"] == 5
    assert saved["is_archived"] is False


def test_capture_memories_without_explicit_remember_phrase(session) -> None:
    semantic_memory = Mock(spec=SemanticMemoryService)
    service = UserMemoryService(session, semantic_memory=semantic_memory)

    captured = service.capture_memories_from_message(
        "My name is Namit and I live in Chandigarh and my favorite language is python"
    )

    keys = {item["key"] for item in captured}
    assert {"name", "location", "favorite_language"} <= keys
    assert service.get_memory("location")["value"] == "Chandigarh"
    assert service.get_memory("favorite_language")["value"] == "Python"
    assert semantic_memory.index_personal_fact.call_count >= 3


def test_upsert_memory_archives_previous_value(session) -> None:
    service = UserMemoryService(session)

    first = service.upsert_memory("college", "SIET")
    second = service.upsert_memory("college", "Thapar")

    archived = service.list_memories(include_archived=True)

    assert first["id"] != second["id"]
    assert service.get_memory("college")["value"] == "Thapar"
    assert any(item["id"] == first["id"] and item["is_archived"] is True for item in archived)


def test_fact_extraction_accepts_pipe_delimited_output(session) -> None:
    service = UserMemoryService(session)
    with patch.object(
        service.llm_engine,
        "generate",
        return_value="Name | Namit\nCollege | SIET\nLocation | Nilokheri",
    ):
        extracted = service._extract_facts_with_llm("my name is namit and i study at siet")

    assert extracted == [
        ("name", "Namit"),
        ("college", "Siet"),
        ("location", "Nilokheri"),
    ]


def test_capture_name_from_i_am_phrase(session) -> None:
    service = UserMemoryService(session)

    captured = service.capture_memories_from_message("i am namit")

    assert any(item["key"] == "name" and item["value"] == "Namit" for item in captured)
    assert service.get_memory("name")["value"] == "Namit"


def test_fact_extraction_rejects_thailand_hallucination(session) -> None:
    service = UserMemoryService(session)

    with patch.object(
        service.llm_engine,
        "generate",
        return_value="Location | Thailand\nCollege | SIET",
    ):
        extracted = service._extract_facts_with_llm("my college is siet")

    assert extracted == []
