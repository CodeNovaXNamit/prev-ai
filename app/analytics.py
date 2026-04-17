"""Behavior analytics and lightweight adaptation signals."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.encryption import EncryptionManager
from app.models import BehaviorEvent


class AnalyticsService:
    """Store feature interactions and derive dashboard insights."""

    def __init__(
        self,
        session: Session,
        encryption_manager: EncryptionManager | None = None,
    ) -> None:
        self.session = session
        self.encryption_manager = encryption_manager or EncryptionManager()

    def track(self, feature: str, action: str, detail: dict[str, Any] | None = None) -> None:
        """Persist a behavior event for personalization and analytics."""
        payload = json.dumps(detail or {}) if detail else None
        event = BehaviorEvent(
            feature=feature,
            action=action,
            detail_encrypted=(
                self.encryption_manager.encrypt(payload) if payload else None
            ),
        )
        self.session.add(event)
        self.session.commit()

    def build_dashboard(
        self,
        tasks: list[dict[str, Any]],
        events: list[dict[str, Any]],
        notes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create derived metrics for the frontend dashboard."""
        behavior_events = (
            self.session.query(BehaviorEvent).order_by(BehaviorEvent.created_at.desc()).limit(50).all()
        )
        weekly_counter: defaultdict[int, int] = defaultdict(int)
        today = datetime.now(tz=timezone.utc).date()
        for event in behavior_events:
            if event.created_at.tzinfo is None:
                event_date = event.created_at.date()
            else:
                event_date = event.created_at.astimezone(timezone.utc).date()
            age = (today - event_date).days
            if 0 <= age < 7:
                weekly_counter[6 - age] += 1

        weekly_activity = [weekly_counter[index] for index in range(7)]
        completed = len([task for task in tasks if task.get("completed")])
        task_count = max(len(tasks), 1)
        tasks_completed_percent = round((completed / task_count) * 100)

        timeline = []
        for item in behavior_events[:4]:
            created_at = item.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            timeline.append(
                {
                    "title": f"{item.feature.title()} {item.action.replace('_', ' ')}",
                    "time": created_at.astimezone(timezone.utc).strftime("%H:%M"),
                    "status": "tracked",
                }
            )

        preferred_feature = "chat"
        if behavior_events:
            preferred_feature = Counter(event.feature for event in behavior_events).most_common(1)[0][0]

        completion_series = []
        for day_offset in range(6, -1, -1):
            boundary = today - timedelta(days=day_offset)
            recent_done = sum(
                1
                for task in tasks
                if task.get("completed") and task.get("updated_at", "").startswith(boundary.isoformat())
            )
            completion_series.append(min(100, recent_done * 20 or tasks_completed_percent))

        return {
            "sessions": len(behavior_events),
            "tasks_completed_percent": tasks_completed_percent,
            "saved_notes": len(notes),
            "scheduled_events": len(events),
            "weekly_activity": weekly_activity,
            "completion_series": completion_series,
            "timeline": timeline or [
                {"title": "Workspace initialized", "time": "00:00", "status": "ready"}
            ],
            "preferred_feature": preferred_feature,
        }
