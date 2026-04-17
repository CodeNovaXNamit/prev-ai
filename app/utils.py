"""Utility helpers used across the application."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    """Return the current UTC time in ISO 8601 format."""
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()


def generate_id() -> str:
    """Generate a compact unique identifier."""
    return uuid4().hex


def truncate_text(text: str, limit: int = 240) -> str:
    """Truncate text without breaking the UI."""
    clean = " ".join(text.split())
    return clean if len(clean) <= limit else f"{clean[: limit - 3].rstrip()}..."


def ensure_list(value: Any) -> list[Any]:
    """Normalize values into a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
