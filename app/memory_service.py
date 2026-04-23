"""Encrypted user fact memory service."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from app.encryption import EncryptionManager
from app.llm_engine import LocalLLMEngine
from app.models import UserMemoryRecord
from app.semantic_memory import SemanticMemoryService
from app.utils import generate_id
from app.utils.sanitizer import sanitize_text


class UserMemoryService:
    """Persist, recall, and semantically index remembered user facts."""

    DIRECT_PATTERNS: tuple[tuple[str, str], ...] = (
        ("name", r"\bmy name is\s+(?P<value>[a-z][a-z\s'-]{0,40})\b"),
        ("name", r"\bi am\s+(?P<value>[a-z][a-z\s'-]{0,40})\b"),
        ("name", r"\bi'm\s+(?P<value>[a-z][a-z\s'-]{0,40})\b"),
        ("location", r"\bi live in\s+(?P<value>[a-z][a-z\s,.'-]{0,60})\b"),
        ("location", r"\bi am from\s+(?P<value>[a-z][a-z\s,.'-]{0,60})\b"),
        ("location", r"\bi'm from\s+(?P<value>[a-z][a-z\s,.'-]{0,60})\b"),
        ("location", r"\bmy city is\s+(?P<value>[a-z][a-z\s,.'-]{0,60})\b"),
        ("college", r"\bi study at\s+(?P<value>[a-z0-9][a-z0-9\s,.'()&-]{0,80})\b"),
        ("college", r"\bi am at\s+(?P<value>[a-z0-9][a-z0-9\s,.'()&-]{0,80}\b(?:college|university|institute|school))"),
        ("degree", r"\bi(?: am|'m)\s+(?:studying|pursuing)\s+(?P<value>[a-z][a-z0-9\s,.'()&-]{0,80})\b"),
        ("degree", r"\bmy degree is\s+(?P<value>[a-z][a-z0-9\s,.'()&-]{0,80})\b"),
        ("occupation", r"\bi work as\s+(?P<value>[a-z][a-z\s'-]{0,60})\b"),
        ("occupation", r"\bi am a[n]?\s+(?P<value>[a-z][a-z\s'-]{0,60})\b"),
        ("cgpa", r"\bmy cgpa is\s+(?P<value>[0-9]+(?:\.[0-9]+)?)\b"),
        ("language_levels", r"\bmy language levels? (?:is|are)\s+(?P<value>[a-z0-9\s,.'-]{0,120})\b"),
        ("interests", r"\bi am interested in\s+(?P<value>[a-z0-9][a-z0-9\s,.'/&-]{0,120})\b"),
        ("interests", r"\bmy interests? (?:is|are)\s+(?P<value>[a-z0-9][a-z0-9\s,.'/&-]{0,120})\b"),
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
            "college",
            ("which college do i study at", "where do i study", "what is my college"),
            "You study at {value}.",
        ),
        (
            "degree",
            ("what degree am i studying", "what is my degree", "what am i studying"),
            "You are studying {value}.",
        ),
        (
            "occupation",
            ("what do i do", "what is my job", "what do i work as", "do you remember my job"),
            "You told me you work as {value}.",
        ),
        ("cgpa", ("what is my cgpa", "show my cgpa"), "Your CGPA is {value}."),
        (
            "language_levels",
            ("what are my language levels", "show my language levels"),
            "Your language levels are {value}.",
        ),
        (
            "interests",
            ("what are my interests", "what am i interested in"),
            "You are interested in {value}.",
        ),
    )
    FACT_SYSTEM_PROMPT = (
        "You are a data extraction tool. Extract facts from the user's message.\n"
        "Output Format: Key | Value\n"
        "Example: Hobby | Coding\n"
        "Rules:\n"
        "1. Do not explain your reasoning.\n"
        "2. Do not mention Thailand or privacy policies.\n"
        "3. Only extract what is explicitly stated.\n"
        "4. If no new fact is found, return 'NO_NEW_FACT'."
    )
    FACT_KEY_ALIASES = {
        "university": "college",
        "college": "college",
        "school": "college",
        "institute": "college",
        "degree": "degree",
        "branch": "degree",
        "course": "degree",
        "name": "name",
        "location": "location",
        "city": "location",
        "hometown": "location",
        "occupation": "occupation",
        "job": "occupation",
        "cgpa": "cgpa",
        "language levels": "language_levels",
        "languages": "language_levels",
        "interest": "interests",
        "interests": "interests",
    }
    ALLOWED_KEYS = {
        "name",
        "location",
        "college",
        "degree",
        "occupation",
        "cgpa",
        "language_levels",
        "interests",
    }
    IMPORTANCE_MAP = {
        "name": 5,
        "college": 5,
        "degree": 5,
        "cgpa": 5,
        "location": 4,
        "occupation": 4,
        "language_levels": 3,
        "interests": 3,
    }
    PERSONAL_CUE_PATTERN = re.compile(
        r"\b(?:my\s+(?:name|city|college|degree|cgpa|language levels?|favorite|interests?)|"
        r"i\s+(?:am\s+[a-z][a-z\s'-]{0,40}|live in|am from|study at|work as|am interested in|am a|am an|am studying|am pursuing)|"
        r"i'm\s+from|remember that my)\b",
        flags=re.IGNORECASE,
    )
    FORBIDDEN_EXTRACTION_WORDS = ("thailand", "set", "bangkok")

    def __init__(
        self,
        session: Session,
        encryption_manager: EncryptionManager | None = None,
        llm_engine: LocalLLMEngine | None = None,
        semantic_memory: SemanticMemoryService | None = None,
    ) -> None:
        self.session = session
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.llm_engine = llm_engine or LocalLLMEngine()
        self.semantic_memory = semantic_memory or SemanticMemoryService()

    def capture_memories_from_message(self, message: str) -> list[dict[str, Any]]:
        """Extract and persist supported user facts from a message."""
        sanitized = sanitize_text(message)
        if sanitized.is_system_log:
            return []
        if self._is_memory_or_profile_query(sanitized.cleaned_text):
            return []
        if not self.PERSONAL_CUE_PATTERN.search(sanitized.cleaned_text):
            return []

        extracted = self._extract_facts_with_llm(sanitized.cleaned_text)
        fallback = self._extract_facts_with_regex(sanitized.cleaned_text)

        merged: dict[str, str] = {}
        for key, value in [*extracted, *fallback]:
            if not value:
                continue
            merged.setdefault(key, value)

        captured: list[dict[str, Any]] = []
        for key, value in merged.items():
            importance = self._infer_importance(key, value)
            stored = self.upsert_memory(key, value, importance=importance)
            self.semantic_memory.index_personal_fact(
                stored["id"],
                self._canonicalize_fact(key, value),
                key=key,
                importance=importance,
                source="user_input",
            )
            captured.append(stored)
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

    def list_memories(self, include_archived: bool = False) -> list[dict[str, Any]]:
        """Return remembered facts."""
        query = self.session.query(UserMemoryRecord)
        if not include_archived:
            query = query.filter(UserMemoryRecord.is_archived.is_(False))
        rows = query.order_by(UserMemoryRecord.updated_at.desc()).all()
        return [self._serialize(row) for row in rows]

    def get_relevant_facts(self, query_text: str, limit: int = 4) -> list[dict[str, Any]]:
        """Return semantically related active facts, highest importance first."""
        semantic_hits = self.semantic_memory.query_personal_facts(query_text, limit=limit)
        if semantic_hits:
            return sorted(semantic_hits, key=lambda item: item.get("importance", 0), reverse=True)[:limit]

        memories = self.list_memories()
        return [
            {"text": self._canonicalize_fact(item["key"], item["value"]), "key": item["key"], "importance": item["importance"]}
            for item in memories[:limit]
        ]

    def build_capture_response(self, message: str, captured: list[dict[str, Any]]) -> str | None:
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

    def get_memory(self, key: str) -> dict[str, Any] | None:
        """Return one active remembered fact by key."""
        row = (
            self.session.query(UserMemoryRecord)
            .filter(UserMemoryRecord.key == key, UserMemoryRecord.is_archived.is_(False))
            .order_by(UserMemoryRecord.updated_at.desc())
            .first()
        )
        return self._serialize(row) if row else None

    def upsert_memory(self, key: str, value: str, importance: int | None = None) -> dict[str, Any]:
        """Insert or update a remembered fact while preserving prior history."""
        normalized_value = self._normalize_value(key, value)
        if not normalized_value:
            raise ValueError("Memory value cannot be empty.")

        active_rows = (
            self.session.query(UserMemoryRecord)
            .filter(UserMemoryRecord.key == key, UserMemoryRecord.is_archived.is_(False))
            .all()
        )
        normalized_importance = importance or self._infer_importance(key, normalized_value)

        for row in active_rows:
            current_value = self.encryption_manager.decrypt(row.value_encrypted)
            if current_value == normalized_value and row.importance == normalized_importance:
                return self._serialize(row)
            row.is_archived = True

        row = UserMemoryRecord(
            id=generate_id(),
            key=key,
            value_encrypted=self.encryption_manager.encrypt(normalized_value),
            importance=normalized_importance,
            is_archived=False,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._serialize(row)

    def _serialize(self, row: UserMemoryRecord) -> dict[str, Any]:
        """Convert an ORM row into a plain payload."""
        return {
            "id": row.id,
            "key": row.key,
            "value": self.encryption_manager.decrypt(row.value_encrypted),
            "importance": row.importance,
            "is_archived": row.is_archived,
        }

    def _extract_facts_with_llm(self, message: str) -> list[tuple[str, str]]:
        if not message.strip():
            return []
        candidate = self.llm_engine.generate(
            self.llm_engine.get_extraction_prompt(message),
            system_prompt=self.FACT_SYSTEM_PROMPT,
            options={"temperature": 0.0, "top_p": 0.3, "num_predict": 120, "repeat_penalty": 1.1},
            include_core_identity=False,
        ).strip()
        candidate = self.validate_extracted_facts(candidate)
        if (
            not candidate
            or candidate.upper() in {"NO_NEW_FACT", "NONE"}
            or "The local model runner is unavailable" in candidate
        ):
            return []

        extracted: list[tuple[str, str]] = []
        for raw_line in candidate.splitlines():
            line = raw_line.strip(" -*\t")
            if not line or "|" not in line:
                continue
            raw_key, raw_value = line.split("|", 1)
            key = self._normalize_fact_key(raw_key)
            if not key:
                continue
            value = self._normalize_value(key, raw_value)
            if key and value:
                extracted.append((key, value))
        return extracted

    def validate_extracted_facts(self, facts_string: str) -> str:
        """Reject extracted facts that contain known hallucinated location terms."""
        lowered = facts_string.lower()
        if any(word in lowered for word in self.FORBIDDEN_EXTRACTION_WORDS):
            return "NONE"
        return facts_string

    def _extract_facts_with_regex(self, message: str) -> list[tuple[str, str]]:
        extracted: list[tuple[str, str]] = []
        seen_keys: set[str] = set()

        for key, pattern in self.DIRECT_PATTERNS:
            match = re.search(pattern, message, flags=re.IGNORECASE)
            if not match:
                continue
            value = self._normalize_value(key, match.group("value"))
            if not value or key in seen_keys:
                continue
            extracted.append((key, value))
            seen_keys.add(key)

        favorite_match = self.FAVORITE_PATTERN.search(message)
        if favorite_match:
            favorite_key = self._favorite_key(favorite_match.group("key"))
            value = self._normalize_value(favorite_key, favorite_match.group("value"))
            if value and favorite_key not in seen_keys:
                extracted.append((favorite_key, value))

        return extracted

    def _normalize_fact_key(self, raw_key: str) -> str:
        normalized = " ".join(raw_key.strip().lower().split())
        mapped = self.FACT_KEY_ALIASES.get(normalized)
        if mapped:
            return mapped
        return normalized.replace(" ", "_") if normalized.startswith("favorite ") else ""

    def _favorite_key(self, raw_key: str) -> str:
        normalized = "_".join(raw_key.strip().lower().split())
        return f"favorite_{normalized}"

    def _canonicalize_fact(self, key: str, value: str) -> str:
        templates = {
            "name": "The user's name is {value}.",
            "location": "The user is from {value}.",
            "college": "The user studies at {value}.",
            "degree": "The user is studying {value}.",
            "occupation": "The user works as {value}.",
            "cgpa": "The user's CGPA is {value}.",
            "language_levels": "The user's language levels are {value}.",
            "interests": "The user is interested in {value}.",
        }
        if key.startswith("favorite_"):
            label = key.removeprefix("favorite_").replace("_", " ")
            return f"The user's favorite {label} is {value}."
        return templates.get(key, "The user shared {key}: {value}.").format(key=key.replace("_", " "), value=value)

    def _infer_importance(self, key: str, value: str) -> int:
        if key.startswith("favorite_"):
            return 3
        if len(value.split()) > 10:
            return 2
        return self.IMPORTANCE_MAP.get(key, 2)

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
            parts = cleaned.split()
            if len(parts) > 3:
                cleaned = " ".join(parts[:3])
        if key == "cgpa":
            return cleaned
        return " ".join(part.capitalize() for part in cleaned.split())

    def _missing_memory_response(self, key: str) -> str:
        labels = {
            "name": "name",
            "location": "location",
            "college": "college",
            "degree": "degree",
            "occupation": "job",
            "cgpa": "cgpa",
            "language_levels": "language levels",
            "interests": "interests",
        }
        return f"I do not have your {labels.get(key, key)} saved yet."

    def _is_memory_or_profile_query(self, message: str) -> bool:
        """Avoid treating user questions as new personal facts."""
        lowered = message.lower().strip()
        if lowered.endswith("?"):
            return True
        if any(phrase in lowered for _, phrases, _ in self.QUERY_PATTERNS for phrase in phrases):
            return True
        if any(
            phrase in lowered
            for phrase in [
                "what do you know about me",
                "show my profile",
                "what do you remember about me",
                "what is my favorite",
                "who am i",
                "do you know my name",
            ]
        ):
            return True
        return False
