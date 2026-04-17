"""Simple local event scheduler."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.encryption import EncryptionManager
from app.models import EventRecord
from app.utils import generate_id


class SchedulerManager:
    """CRUD operations for calendar events."""

    def __init__(
        self,
        session: Session,
        encryption_manager: EncryptionManager | None = None,
    ) -> None:
        self.session = session
        self.encryption_manager = encryption_manager or EncryptionManager()

    def add_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        location: str = "",
        notes: str = "",
    ) -> dict[str, Any]:
        """Create a calendar event."""
        event = EventRecord(
            id=generate_id(),
            title_encrypted=self.encryption_manager.encrypt(title.strip()),
            start_time=datetime.fromisoformat(start_time),
            end_time=datetime.fromisoformat(end_time),
            location_encrypted=self.encryption_manager.encrypt(location.strip()),
            notes_encrypted=self.encryption_manager.encrypt(notes.strip()),
        )
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return self._serialize(event)

    def update_event(self, event_id: str, **updates: Any) -> dict[str, Any]:
        """Update an existing event."""
        event = self.session.get(EventRecord, event_id)
        if not event:
            raise KeyError(f"Event '{event_id}' was not found.")
        if updates.get("title") is not None:
            event.title_encrypted = self.encryption_manager.encrypt(str(updates["title"]).strip())
        if updates.get("start_time") is not None:
            event.start_time = datetime.fromisoformat(str(updates["start_time"]))
        if updates.get("end_time") is not None:
            event.end_time = datetime.fromisoformat(str(updates["end_time"]))
        if updates.get("location") is not None:
            event.location_encrypted = self.encryption_manager.encrypt(str(updates["location"]).strip())
        if updates.get("notes") is not None:
            event.notes_encrypted = self.encryption_manager.encrypt(str(updates["notes"]).strip())
        self.session.commit()
        self.session.refresh(event)
        return self._serialize(event)

    def list_events(self) -> list[dict[str, Any]]:
        """List all events."""
        events = self.session.query(EventRecord).order_by(EventRecord.start_time.asc()).all()
        return [self._serialize(event) for event in events]

    def delete_event(self, event_id: str) -> bool:
        """Delete an event."""
        event = self.session.get(EventRecord, event_id)
        if not event:
            return False
        self.session.delete(event)
        self.session.commit()
        return True

    def _serialize(self, event: EventRecord) -> dict[str, Any]:
        """Convert an ORM row into an API payload."""
        return {
            "id": event.id,
            "title": self.encryption_manager.decrypt(event.title_encrypted),
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": self.encryption_manager.decrypt(event.location_encrypted),
            "notes": self.encryption_manager.decrypt(event.notes_encrypted),
            "created_at": event.created_at.isoformat(),
            "updated_at": event.updated_at.isoformat(),
        }
