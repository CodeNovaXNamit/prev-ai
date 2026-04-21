"""Encrypted chat memory service."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.encryption import EncryptionManager
from app.models import ChatMessageRecord
from app.utils import generate_id
from app.utils.sanitizer import sanitize_text


class ChatMemoryService:
    """Persist and retrieve encrypted chat history."""

    def __init__(
        self,
        session: Session,
        encryption_manager: EncryptionManager | None = None,
    ) -> None:
        self.session = session
        self.encryption_manager = encryption_manager or EncryptionManager()

    def add_message(self, role: str, content: str) -> dict[str, Any]:
        """Store a chat message after applying input sanitization."""
        sanitized = sanitize_text(content) if role == "user" else None
        stored_content = (sanitized.cleaned_text if sanitized is not None else content).strip()
        if not stored_content:
            stored_content = content.strip()

        message = ChatMessageRecord(
            id=generate_id(),
            role=role,
            content_encrypted=self.encryption_manager.encrypt(stored_content),
            is_system_log=bool(sanitized.is_system_log) if sanitized is not None else False,
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return self._serialize(message)

    def list_recent_messages(self, limit: int = 5) -> list[dict[str, Any]]:
        """Return recent non-log chat messages in chronological order."""
        rows = (
            self.session.query(ChatMessageRecord)
            .filter(ChatMessageRecord.is_system_log.is_(False))
            .order_by(ChatMessageRecord.created_at.desc())
            .limit(limit)
            .all()
        )
        return [self._serialize(row) for row in reversed(rows)]

    def _serialize(self, row: ChatMessageRecord) -> dict[str, Any]:
        """Convert an ORM row into an API payload."""
        return {
            "id": row.id,
            "role": row.role,
            "content": self.encryption_manager.decrypt(row.content_encrypted),
            "is_system_log": row.is_system_log,
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
        }
