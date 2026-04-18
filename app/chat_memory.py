"""Encrypted chat memory service."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.encryption import EncryptionManager
from app.models import ChatMessageRecord
from app.utils import generate_id


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
        """Store a chat message."""
        message = ChatMessageRecord(
            id=generate_id(),
            role=role,
            content_encrypted=self.encryption_manager.encrypt(content.strip()),
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return self._serialize(message)

    def list_recent_messages(self, limit: int = 8) -> list[dict[str, Any]]:
        """Return recent chat messages in chronological order."""
        rows = (
            self.session.query(ChatMessageRecord)
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
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
        }
