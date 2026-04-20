"""Structured SQL-backed ground truth for profile facts and projects."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.encryption import EncryptionManager
from app.models import ProjectRegistryRecord, UserProfileRecord


class GroundTruthService:
    """Store and query immutable facts from SQL before any LLM call."""

    PROFILE_QUERY_MAP: tuple[tuple[str, tuple[str, ...], str], ...] = (
        ("name", ("what is my name", "who am i", "do you know my name"), "Your name is {value}."),
        ("location", ("where do i live", "where am i from", "what is my city"), "You are from {value}."),
        ("cgpa", ("what is my cgpa", "my cgpa", "show my cgpa"), "Your CGPA is {value}."),
        (
            "language_levels",
            ("what are my language levels", "show my language levels", "my language levels"),
            "Your language levels are {value}.",
        ),
    )

    def __init__(
        self,
        session: Session,
        encryption_manager: EncryptionManager | None = None,
    ) -> None:
        self.session = session
        self.encryption_manager = encryption_manager or EncryptionManager()

    def sync_profile_memories(self, memories: list[dict[str, str]]) -> None:
        """Mirror captured user facts into the structured profile table."""
        for memory in memories:
            self.upsert_profile(memory["key"], memory["value"])

    def upsert_profile(self, attribute: str, value: str) -> dict[str, str]:
        """Insert or update a profile fact."""
        row = self.session.get(UserProfileRecord, attribute)
        if row is None:
            row = UserProfileRecord(
                attribute=attribute,
                value_encrypted=self.encryption_manager.encrypt(value.strip()),
            )
            self.session.add(row)
        else:
            row.value_encrypted = self.encryption_manager.encrypt(value.strip())
        self.session.commit()
        self.session.refresh(row)
        return self._serialize_profile(row)

    def list_profile(self) -> list[dict[str, str]]:
        """Return all structured profile facts."""
        rows = self.session.query(UserProfileRecord).order_by(UserProfileRecord.attribute.asc()).all()
        return [self._serialize_profile(row) for row in rows]

    def answer_profile_query(self, message: str) -> str | None:
        """Answer profile queries from structured SQL facts."""
        lowered = message.lower().strip()

        if "remember my name" in lowered and "my name is" not in lowered:
            return "Tell me your name in one message, and I'll save it."

        for attribute, phrases, template in self.PROFILE_QUERY_MAP:
            if any(phrase in lowered for phrase in phrases):
                fact = self.get_profile(attribute)
                if fact is not None:
                    return template.format(value=fact["value"])
                return f"I do not have your {attribute.replace('_', ' ')} saved yet."

        return None

    def get_profile(self, attribute: str) -> dict[str, str] | None:
        """Fetch a single profile fact."""
        row = self.session.get(UserProfileRecord, attribute)
        return self._serialize_profile(row) if row is not None else None

    def upsert_project(
        self,
        project_id: str,
        name: str,
        team_members: str = "",
        status: str = "active",
    ) -> dict[str, str]:
        """Insert or update one project registry row."""
        row = self.session.get(ProjectRegistryRecord, project_id)
        if row is None:
            row = ProjectRegistryRecord(
                project_id=project_id,
                name=name.strip(),
                team_members_encrypted=self.encryption_manager.encrypt(team_members.strip()),
                status=status.strip() or "active",
            )
            self.session.add(row)
        else:
            row.name = name.strip()
            row.team_members_encrypted = self.encryption_manager.encrypt(team_members.strip())
            row.status = status.strip() or "active"
        self.session.commit()
        self.session.refresh(row)
        return self._serialize_project(row)

    def list_projects(self) -> list[dict[str, str]]:
        """Return all projects."""
        rows = self.session.query(ProjectRegistryRecord).order_by(ProjectRegistryRecord.name.asc()).all()
        return [self._serialize_project(row) for row in rows]

    def resolve_project(self, message: str) -> dict[str, str] | None:
        """Find the best project match from a message."""
        normalized = self._normalize_text(message)
        if not normalized:
            return None

        rows = self.session.query(ProjectRegistryRecord).all()
        exact = None
        partial = None
        for row in rows:
            candidates = [row.project_id, row.name]
            normalized_candidates = [self._normalize_text(candidate) for candidate in candidates if candidate]
            if any(normalized == candidate for candidate in normalized_candidates):
                exact = row
                break
            if any(candidate in normalized or normalized in candidate for candidate in normalized_candidates):
                partial = row
        chosen = exact or partial
        return self._serialize_project(chosen) if chosen is not None else None

    def answer_project_query(self, message: str) -> str | None:
        """Answer project questions directly from SQL."""
        project = self.resolve_project(message)
        if project is None:
            return None
        members = project["team_members"] or "No team members saved"
        return (
            f"Project {project['name']} [{project['project_id']}] is {project['status']}. "
            f"Team members: {members}."
        )

    def _serialize_profile(self, row: UserProfileRecord | None) -> dict[str, str]:
        if row is None:
            return {}
        return {
            "attribute": row.attribute,
            "value": self.encryption_manager.decrypt(row.value_encrypted),
        }

    def _serialize_project(self, row: ProjectRegistryRecord) -> dict[str, str]:
        return {
            "project_id": row.project_id,
            "name": row.name,
            "team_members": self.encryption_manager.decrypt(row.team_members_encrypted),
            "status": row.status,
        }

    def _normalize_text(self, value: str) -> str:
        cleaned = re.sub(r"[^a-z0-9\s]", " ", value.lower())
        return " ".join(cleaned.split())
