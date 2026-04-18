"""Encrypted user fact memory service."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from app.encryption import EncryptionManager
from app.models import UserMemoryRecord
from app.utils import generate_id


class UserMemoryService:
    """Persist and recall small remembered user facts."""

    DIRECT_PATTERNS: tuple[tuple[str, str], ...] = (
        ("name", r"\bmy name is\s+(?P<value>[a-z][a-z\s'-]{0,40})\b"),
        ("location", r"\bi live in\s+(?P<value>[a-z][a-z\s,.'-]{0,60})\b"),
        ("location", r"\bi am from\s+(?P<value>[a-z][a-z\s,.'-]{0,60})\b"),
        ("location", r"\bi'm from\s+(?P<value>[a-z][a-z\s,.'-]{0,60})\b"),
        ("location", r"\bmy city is\s+(?P<value>[a-z][a-z\s,.'-]{0,60})\b"),
        ("occupation", r"\bi work as\s+(?P<value>[a-z][a-z\s'-]{0,60})\b"),
        ("occupation", r"\bi am a[n]?\s+(?P<value>[a-z][a-z\s'-]{0,60})\b"),
    )
    FAVORITE_PATTERN = re.compile(
        r"\bmy favorite\s+(?P<key>[a-z][a-z\s'-]{0,30})\s+is\s+(?P<value>[a-z0-9][a-z0-9\s,.'-]{0,60})\b",
        flags=re.IGNORECASE,
    )
    QUERY_PATTERNS: tuple[tuple[str, tuple[str, ...], str], ...] = (
        ("name", ("what is my name", "what's my name", "do you remember my name"), "Your name is {value}."),
        (
            "location",
            ("where do i live", "where am i from", "what is my city", "do you know where i live"),
            "You told me you are from {value}.",
        ),
        (
            "occupation",
            ("what do i do", "what is my job", "what do i work as", "do you remember my job"),
            "You told me you work as {value}.",
        ),
    )

    def __init__(
        self,
        session: Session,
        encryption_manager: EncryptionManager | None = None,
    ) -> None:
        self.session = session
        self.encryption_manager = encryption_manager or EncryptionManager()

    def capture_memories_from_message(self, message: str) -> list[dict[str, str]]:
        """Extract and persist supported user facts from a message."""
        captured: list[dict[str, str]] = []
        seen_keys: set[str] = set()

        for key, pattern in self.DIRECT_PATTERNS:
            match = re.search(pattern, message, flags=re.IGNORECASE)
            if not match:
                continue
            value = self._normalize_value(key, match.group("value"))
            if not value or key in seen_keys:
                continue
            captured.append(self.upsert_memory(key, value))
            seen_keys.add(key)

        favorite_match = self.FAVORITE_PATTERN.search(message)
        if favorite_match:
            favorite_key = self._favorite_key(favorite_match.group("key"))
            value = self._normalize_value(favorite_key, favorite_match.group("value"))
            if value and favorite_key not in seen_keys:
                captured.append(self.upsert_memory(favorite_key, value))

        return captured

    def answer_memory_query(self, message: str) -> str | None:
        """Answer supported memory questions directly from stored facts."""
        lowered = message.lower().strip()
        if any(phrase in lowered for phrase in ["what do you know about me", "show my profile", "what do you remember about me"]):
            memories = self.list_memories()
            if not memories:
                return "I do not have any personal details saved yet."
            joined = ", ".join(f"{item['key'].replace('_', ' ')}: {item['value']}" for item in memories[:8])
            return f"I remember these details about you: {joined}."

        for key, phrases, template in self.QUERY_PATTERNS:
            if any(phrase in lowered for phrase in phrases):
                memory = self.get_memory(key)
                if memory:
                    return template.format(value=memory["value"])
                return self._missing_memory_response(key)

        favorite_match = re.search(
            r"\bwhat is my favorite\s+(?P<key>[a-z][a-z\s'-]{0,30})\b",
            lowered,
            flags=re.IGNORECASE,
        )
        if favorite_match:
            favorite_key = self._favorite_key(favorite_match.group("key"))
            memory = self.get_memory(favorite_key)
            if memory:
                label = favorite_match.group("key").strip()
                return f"Your favorite {label} is {memory['value']}."
            label = favorite_match.group("key").strip()
            return f"I do not have your favorite {label} saved yet."

        return None

    def list_memories(self) -> list[dict[str, str]]:
        """Return all remembered facts."""
        rows = self.session.query(UserMemoryRecord).order_by(UserMemoryRecord.updated_at.desc()).all()
        return [self._serialize(row) for row in rows]

    def build_capture_response(self, message: str, captured: list[dict[str, str]]) -> str | None:
        """Return a same-turn response when a user shares personal details."""
        if not captured:
            return None

        name = next((item["value"] for item in captured if item["key"] == "name"), None)
        lowered = message.lower()
        if "greet me" in lowered or "say hello" in lowered:
            if name:
                return f"Hello, {name}. I'll remember that."
            return "Hello. I'll remember that."
        if any(token in lowered for token in ["who am i", "what is my name"]):
            if name:
                return f"You're {name}. I'll remember that."
        joined = ", ".join(f"{item['key'].replace('_', ' ')} = {item['value']}" for item in captured)
        return f"I'll remember that: {joined}."

    def get_memory(self, key: str) -> dict[str, str] | None:
        """Return one remembered fact by key."""
        row = self.session.query(UserMemoryRecord).filter(UserMemoryRecord.key == key).one_or_none()
        return self._serialize(row) if row else None

    def upsert_memory(self, key: str, value: str) -> dict[str, str]:
        """Insert or update a remembered fact."""
        row = self.session.query(UserMemoryRecord).filter(UserMemoryRecord.key == key).one_or_none()
        if row is None:
            row = UserMemoryRecord(
                id=generate_id(),
                key=key,
                value_encrypted=self.encryption_manager.encrypt(value),
            )
            self.session.add(row)
        else:
            row.value_encrypted = self.encryption_manager.encrypt(value)
        self.session.commit()
        self.session.refresh(row)
        return self._serialize(row)

    def _serialize(self, row: UserMemoryRecord) -> dict[str, str]:
        """Convert an ORM row into a plain payload."""
        return {
            "id": row.id,
            "key": row.key,
            "value": self.encryption_manager.decrypt(row.value_encrypted),
        }

    def _favorite_key(self, raw_key: str) -> str:
        normalized = "_".join(raw_key.strip().lower().split())
        return f"favorite_{normalized}"

    def _normalize_value(self, key: str, raw_value: str) -> str:
        cleaned = raw_value.strip(" .,!?")
        cleaned = re.split(
            r"\b(?:greet me|remember(?:\s+it)?|please|thanks|thank you|and|but)\b",
            cleaned,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0].strip(" .,!?")
        if not cleaned:
            return ""
        if key == "name":
            return " ".join(part.capitalize() for part in cleaned.split())
        return " ".join(part.capitalize() for part in cleaned.split())

    def _missing_memory_response(self, key: str) -> str:
        labels = {
            "name": "name",
            "location": "location",
            "occupation": "job",
        }
        return f"I do not have your {labels.get(key, key)} saved yet."
