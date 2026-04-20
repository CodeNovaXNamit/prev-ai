"""Simple local event scheduler."""

from __future__ import annotations

from datetime import datetime, timedelta
import re
from typing import Any

from sqlalchemy.orm import Session

from app.encryption import EncryptionManager
from app.models import EventRecord
from app.utils import generate_id


class SchedulerManager:
    """CRUD operations for calendar events."""

    EVENT_KEYWORDS = ("meeting", "appointment", "call", "interview", "demo", "session", "event")
    SAVE_PATTERNS = (
        r"\bi have\b",
        r"\bschedule\b",
        r"\badd\b",
        r"\bbook\b",
        r"\bset up\b",
        r"\bsave\b",
        r"\bcreate\b",
    )

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

    def create_events_from_message(self, message: str, now: datetime | None = None) -> list[dict[str, Any]]:
        """Persist meeting-style event intents extracted from chat."""
        candidate = self._extract_event_candidate(message, now=now)
        if candidate is None:
            return []
        return [self.add_event(**candidate)]

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

    def _extract_event_candidate(
        self,
        message: str,
        now: datetime | None = None,
    ) -> dict[str, str] | None:
        """Infer a dated event from a natural-language chat message."""
        normalized = " ".join(message.strip().split())
        lowered = normalized.lower()
        if not any(re.search(pattern, lowered) for pattern in self.SAVE_PATTERNS):
            return None
        keyword = next((item for item in self.EVENT_KEYWORDS if item in lowered), None)
        if keyword is None:
            return None

        event_date = self._extract_event_date(normalized, now=now)
        event_time = self._extract_event_time(normalized)
        if event_date is None or event_time is None:
            return None

        start_time = datetime.combine(event_date.date(), event_time)
        end_time = start_time + timedelta(hours=1)
        title = self._extract_event_title(normalized, keyword)
        location = self._extract_location(normalized)
        return {
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": location,
            "notes": "Captured from chat",
        }

    def _extract_event_title(self, message: str, keyword: str) -> str:
        """Build a readable event title from the message."""
        match = re.search(
            rf"\b{keyword}\b(?:\s+with\s+(?P<subject>.+?))?(?=\s+\b(?:on|at|in)\b|[.,!?]|$)",
            message,
            flags=re.IGNORECASE,
        )
        subject = ""
        if match and match.group("subject"):
            subject = match.group("subject").strip(" .")
        base = keyword.capitalize()
        if subject:
            return f"{base} with {subject[:80]}"
        return base

    def _extract_event_date(self, message: str, now: datetime | None = None) -> datetime | None:
        """Extract a date from day-month or month-day phrasing."""
        now = now or datetime.now()
        patterns = (
            r"\b(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?P<month>january|february|march|april|may|june|july|august|september|october|november|december)(?:\s+(?P<year>\d{4}))?\b",
            r"\b(?P<month>january|february|march|april|may|june|july|august|september|october|november|december)\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?(?:\s+(?P<year>\d{4}))?\b",
        )
        for pattern in patterns:
            match = re.search(pattern, message, flags=re.IGNORECASE)
            if not match:
                continue
            month = match.group("month").title()
            day = int(match.group("day"))
            year = int(match.group("year")) if match.groupdict().get("year") else now.year
            try:
                parsed = datetime.strptime(f"{month} {day} {year}", "%B %d %Y")
            except ValueError:
                continue
            if match.groupdict().get("year") is None and parsed.date() < now.date():
                parsed = parsed.replace(year=parsed.year + 1)
            return parsed
        return None

    def _extract_event_time(self, message: str) -> datetime.time | None:
        """Extract a clock time from the message."""
        match = re.search(
            r"\bat\s+(?P<time>\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b",
            message,
            flags=re.IGNORECASE,
        )
        if not match:
            return None
        raw_time = re.sub(r"\s+", "", match.group("time").lower())
        formats = ("%I%p", "%I:%M%p", "%H:%M", "%H")
        for fmt in formats:
            try:
                return datetime.strptime(raw_time, fmt).time()
            except ValueError:
                continue
        return None

    def _extract_location(self, message: str) -> str:
        """Extract a simple trailing location clause."""
        patterns = (
            r"\bat\s+location\s+(?P<location>[a-z][a-z\s.'-]{1,80})(?=$|[.,!?])",
            r"\blocation\s+(?P<location>[a-z][a-z\s.'-]{1,80})(?=$|[.,!?])",
            r"\bin\s+(?P<location>[a-z][a-z\s.'-]{1,80})(?=$|[.,!?])",
            r"\bat\s+(?P<location>[a-z][a-z\s.'-]{1,80})(?=$|[.,!?])",
        )
        for pattern in patterns:
            match = re.search(pattern, message, flags=re.IGNORECASE)
            if not match:
                continue
            return " ".join(match.group("location").strip(" .").split()).title()
        return ""
