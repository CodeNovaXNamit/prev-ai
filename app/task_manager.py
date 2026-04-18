"""Task management logic."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from app.encryption import EncryptionManager
from app.models import TaskRecord
from app.utils import generate_id


class TaskManager:
    """CRUD operations for encrypted task records."""

    COMPLETION_PATTERNS = (
        r"\bmark\s+(?P<title>.+?)\s+as\s+(?:completed|done|finished)\b",
        r"\bcomplete\s+(?P<title>.+?)\b",
        r"\bfinished\s+(?P<title>.+?)\b",
        r"\bdone with\s+(?P<title>.+?)\b",
    )
    REFERENCE_PATTERNS = (
        r"\bthis task\b",
        r"\bthis todo\b",
        r"\bthis item\b",
        r"\bit is\b.*\b(?:completed|done|finished)\b",
        r"\bit got\b.*\b(?:completed|done|finished)\b",
        r"\bthis tasks?\b.*\b(?:completed|done|finished)\b",
    )

    def __init__(
        self,
        session: Session,
        encryption_manager: EncryptionManager | None = None,
    ) -> None:
        self.session = session
        self.encryption_manager = encryption_manager or EncryptionManager()

    def add_task(
        self,
        title: str,
        description: str = "",
        due_date: str | None = None,
        priority: str = "medium",
        completed: bool = False,
    ) -> dict[str, Any]:
        """Create a new task."""
        task = TaskRecord(
            id=generate_id(),
            title_encrypted=self.encryption_manager.encrypt(title.strip()),
            description_encrypted=self.encryption_manager.encrypt(description.strip()),
            due_date=due_date,
            priority=priority,
            completed=completed,
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return self._serialize(task)

    def update_task(self, task_id: str, **updates: Any) -> dict[str, Any]:
        """Update an existing task."""
        task = self.session.get(TaskRecord, task_id)
        if not task:
            raise KeyError(f"Task '{task_id}' was not found.")
        if updates.get("title") is not None:
            task.title_encrypted = self.encryption_manager.encrypt(str(updates["title"]).strip())
        if updates.get("description") is not None:
            task.description_encrypted = self.encryption_manager.encrypt(str(updates["description"]).strip())
        if "due_date" in updates:
            task.due_date = updates["due_date"]
        if updates.get("priority") is not None:
            task.priority = str(updates["priority"])
        if updates.get("completed") is not None:
            task.completed = bool(updates["completed"])
        self.session.commit()
        self.session.refresh(task)
        return self._serialize(task)

    def list_tasks(self) -> list[dict[str, Any]]:
        """Return all tasks."""
        tasks = self.session.query(TaskRecord).order_by(TaskRecord.updated_at.desc()).all()
        return [self._serialize(task) for task in tasks]

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        task = self.session.get(TaskRecord, task_id)
        if not task:
            return False
        self.session.delete(task)
        self.session.commit()
        return True

    def create_tasks_from_message(self, message: str) -> list[dict[str, Any]]:
        """Persist task intents extracted from a chat message."""
        candidates = self._extract_task_candidates(message)
        created: list[dict[str, Any]] = []
        for candidate in candidates:
            created.append(
                self.add_task(
                    title=candidate,
                    description="Captured from chat",
                    priority="medium",
                    completed=False,
                )
            )
        return created

    def complete_tasks_from_message(self, message: str) -> list[dict[str, Any]]:
        """Mark tasks complete when the user uses completion phrasing in chat."""
        normalized = " ".join(message.strip().split())

        for pattern in self.COMPLETION_PATTERNS:
            match = re.search(pattern, normalized, flags=re.IGNORECASE)
            if not match:
                continue
            fragment = match.group("title").strip(" .")
            task = self._find_task_for_completion(fragment)
            if task is not None:
                return [self.update_task(task["id"], completed=True)]

        if any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in self.REFERENCE_PATTERNS):
            latest_open = next((task for task in self.list_tasks() if not task.get("completed")), None)
            if latest_open is not None:
                return [self.update_task(latest_open["id"], completed=True)]

        return []

    def _extract_task_candidates(self, message: str) -> list[str]:
        """Infer tasks from explicit reminder-style user phrasing."""
        normalized = " ".join(message.strip().split())
        patterns = [
            r"(?:add task|create task|todo|to-do|remember to|task:)\s+(?P<title>.+)",
            r"(?:i need to|need to)\s+(?P<title>.+)",
            r"(?:remind me to|please remind me to|dont let me forget to|don't let me forget to)\s+(?P<title>.+)",
            r"(?:save (?:this )?as a task|make (?:this )?a task)\s*:?\s*(?P<title>.+)",
        ]
        candidates: list[str] = []
        for pattern in patterns:
            match = re.search(pattern, normalized, flags=re.IGNORECASE)
            if not match:
                continue
            fragment = match.group("title").strip(" .")
            parts = re.split(r"\s*(?:,| and )\s*", fragment)
            for part in parts:
                title = part.strip(" .")
                if len(title) >= 3:
                    candidates.append(title[:160])
            if candidates:
                break
        return candidates

    def _find_task_for_completion(self, fragment: str) -> dict[str, Any] | None:
        """Return the best incomplete task match for a completion phrase."""
        needle = self._normalize_text(fragment)
        if not needle:
            return None

        incomplete = [task for task in self.list_tasks() if not task.get("completed")]
        for task in incomplete:
            title = self._normalize_text(str(task.get("title", "")))
            if needle == title:
                return task

        for task in incomplete:
            title = self._normalize_text(str(task.get("title", "")))
            if needle in title or title in needle:
                return task

        return None

    def _normalize_text(self, value: str) -> str:
        """Lowercase and collapse punctuation for fuzzy task matching."""
        cleaned = re.sub(r"[^a-z0-9\s]", " ", value.lower())
        return " ".join(cleaned.split())

    def _serialize(self, task: TaskRecord) -> dict[str, Any]:
        """Convert an ORM row into an API payload."""
        return {
            "id": task.id,
            "title": self.encryption_manager.decrypt(task.title_encrypted),
            "description": self.encryption_manager.decrypt(task.description_encrypted),
            "due_date": task.due_date,
            "priority": task.priority,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
