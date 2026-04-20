"""Local LLM integration via Ollama."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any

import requests

from app.config import get_settings


class LocalLLMEngine:
    """Wrapper for a local Ollama model with deterministic offline fallbacks."""

    _availability_cache: dict[tuple[str, str], tuple[float, bool]] = {}
    _availability_ttl_seconds = 5.0

    def __init__(
        self,
        model_name: str | None = None,
        ollama_url: str | None = None,
        timeout: int | None = None,
    ) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.model_name
        self.ollama_url = (ollama_url or settings.ollama_url).rstrip("/")
        self.timeout = timeout or settings.request_timeout

    def is_available(self) -> bool:
        """Check whether the local Ollama service is reachable."""
        cache_key = (self.model_name, self.ollama_url)
        now = datetime.now().timestamp()
        cached = self._availability_cache.get(cache_key)
        if cached and now - cached[0] < self._availability_ttl_seconds:
            return cached[1]

        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            response.raise_for_status()
            payload = response.json()
            models = payload.get("models", [])
            available = any(model.get("name", "").startswith(self.model_name) for model in models) or bool(models)
            self._availability_cache[cache_key] = (now, available)
            return available
        except requests.RequestException:
            self._availability_cache[cache_key] = (now, False)
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> str:
        """Generate text locally, falling back to a deterministic local response."""
        payload: dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 220,
            },
        }
        if options:
            payload["options"].update(options)
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip() or self._fallback(prompt)
        except requests.RequestException:
            return self._fallback(prompt)

    def chat(self, message: str, context: dict[str, Any] | None = None) -> tuple[str, str]:
        """Respond conversationally using the local model."""
        if not self.is_available():
            return self._chat_fallback(message, context or {}), "fallback"

        prompt = (
            "You are a privacy-first personal AI assistant running entirely on-device. "
            "Answer only the user's current request. "
            "Use only the local context explicitly provided below when it is relevant. "
            "Do not mention or reuse unrelated prior conversation, notes, user facts, or troubleshooting details.\n\n"
        )
        filtered_context = self._select_context_for_message(message, context or {})
        if filtered_context:
            prompt += self._build_context_block(filtered_context)
        prompt += f"User message:\n{message}\n"
        return self.generate(prompt), "ollama"

    def answer_from_local_context(self, message: str, context: dict[str, Any]) -> str | None:
        """Answer directly from stored local context when possible."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["schedule", "event", "calendar", "meeting", "appointment"]):
            return self._format_schedule_for_query(context.get("events", []), message)

        if any(word in message_lower for word in ["task", "todo", "to-do"]):
            return self._format_tasks(context.get("tasks", []))

        if any(word in message_lower for word in ["note", "summary", "summarize"]):
            return self._format_notes(context.get("notes", []))

        return None

    def _fallback(self, prompt: str) -> str:
        """Local deterministic fallback when Ollama is unavailable."""
        if "summary" in prompt.lower():
            return "Local summary fallback: Ollama is unavailable, but the note was processed locally."
        return self._chat_fallback(prompt, {})

    def _chat_fallback(self, message: str, context: dict[str, Any]) -> str:
        """Answer basic assistant questions directly from local structured data."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["schedule", "event", "calendar", "meeting"]):
            return self._format_schedule(context.get("events", []))

        if any(word in message_lower for word in ["task", "todo", "to-do"]):
            return self._format_tasks(context.get("tasks", []))

        if any(word in message_lower for word in ["note", "summary", "summarize"]):
            return self._format_notes(context.get("notes", []))

        if any(word in message_lower for word in ["remember", "previous", "earlier", "history"]):
            return self._format_recent_messages(context.get("recent_messages", []))

        return (
            "Ollama is not running, so full free-form chat is unavailable. "
            "I stayed fully offline. I can still answer from your local tasks, schedule, and notes."
        )

    def _build_context_block(self, context: dict[str, Any]) -> str:
        """Convert structured context into a prompt-safe text block."""
        lines = ["Relevant local context:"]
        if context.get("tasks"):
            lines.append(f"Tasks: {context['tasks']}")
        if context.get("events"):
            lines.append(f"Events: {context['events']}")
        if context.get("notes"):
            lines.append(f"Notes: {context['notes']}")
        if context.get("semantic_notes"):
            lines.append(f"Semantic notes: {context['semantic_notes']}")
        if context.get("project"):
            lines.append(f"Project: {context['project']}")
        if context.get("recent_messages"):
            lines.append(f"Recent chat memory: {context['recent_messages']}")
        if context.get("remembered_facts"):
            lines.append(f"Remembered user facts: {context['remembered_facts']}")
        return "\n".join(lines) + "\n\n"

    def _select_context_for_message(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Keep only the context that is directly relevant to the current request."""
        message_lower = message.lower()
        selected: dict[str, Any] = {}

        if any(word in message_lower for word in ["schedule", "event", "calendar", "meeting", "appointment"]):
            if context.get("events"):
                selected["events"] = context["events"]

        if any(word in message_lower for word in ["task", "todo", "to-do"]):
            if context.get("tasks"):
                selected["tasks"] = context["tasks"]

        if any(word in message_lower for word in ["note", "summary", "summarize", "document", "file", "text"]):
            if context.get("notes"):
                selected["notes"] = context["notes"]
            if context.get("semantic_notes"):
                selected["semantic_notes"] = context["semantic_notes"]

        if any(word in message_lower for word in ["remember", "previous", "earlier", "history"]):
            if context.get("recent_messages"):
                selected["recent_messages"] = context["recent_messages"]

        if any(word in message_lower for word in ["project", "hvac", "flood"]):
            if context.get("project"):
                selected["project"] = context["project"]
            if context.get("semantic_notes"):
                selected["semantic_notes"] = context["semantic_notes"]

        if any(
            phrase in message_lower
            for phrase in [
                "what do you know about me",
                "show my profile",
                "what do you remember about me",
                "favorite",
                "my name",
                "where do i live",
                "where am i from",
                "what is my city",
                "what do i do",
                "what is my job",
            ]
        ):
            if context.get("remembered_facts"):
                selected["remembered_facts"] = context["remembered_facts"]

        return selected

    def _format_schedule(self, events: list[dict[str, Any]]) -> str:
        """Format saved events into a readable offline answer."""
        if not events:
            return "Your local schedule is empty."

        normalized = sorted(events, key=lambda event: event.get("start_time", ""))
        lines = ["Your local schedule:"]
        for event in normalized[:5]:
            start_time = self._format_datetime(event.get("start_time", ""))
            end_time = self._format_datetime(event.get("end_time", ""))
            location = event.get("location") or "No location"
            lines.append(f"- {event.get('title', 'Untitled event')}: {start_time} to {end_time} at {location}")
        return "\n".join(lines)

    def _format_schedule_for_query(self, events: list[dict[str, Any]], message: str) -> str:
        """Format schedule results with optional date/time filtering."""
        if not events:
            return "Your local schedule is empty."

        filtered = events
        query_date = self._extract_date_from_message(message)
        if query_date is not None:
            filtered = [
                event for event in filtered if self._event_matches_date(event.get("start_time", ""), query_date)
            ]

        message_lower = message.lower()
        if "morning" in message_lower:
            filtered = [
                event for event in filtered if self._event_hour(event.get("start_time", "")) is not None and self._event_hour(event.get("start_time", "")) < 12
            ]
        elif "afternoon" in message_lower:
            filtered = [
                event for event in filtered if self._event_hour(event.get("start_time", "")) is not None and 12 <= self._event_hour(event.get("start_time", "")) < 18
            ]
        elif "evening" in message_lower or "night" in message_lower:
            filtered = [
                event for event in filtered if self._event_hour(event.get("start_time", "")) is not None and self._event_hour(event.get("start_time", "")) >= 18
            ]

        if not filtered:
            if query_date is not None:
                return f"You do not have any saved appointments for {query_date.strftime('%B %d')} in the requested time window."
            return "You do not have any saved appointments matching that request."

        normalized = sorted(filtered, key=lambda event: event.get("start_time", ""))
        lines = ["Your saved appointments:"]
        for event in normalized[:5]:
            start_time = self._format_datetime(event.get("start_time", ""))
            end_time = self._format_datetime(event.get("end_time", ""))
            location = event.get("location") or "No location"
            lines.append(f"- {event.get('title', 'Untitled event')}: {start_time} to {end_time} at {location}")
        return "\n".join(lines)

    def _format_tasks(self, tasks: list[dict[str, Any]]) -> str:
        """Format saved tasks into a readable offline answer."""
        if not tasks:
            return "You have no local tasks saved."

        lines = ["Your local tasks:"]
        for task in tasks[:5]:
            status = "done" if task.get("completed") else "pending"
            due_date = task.get("due_date") or "no due date"
            lines.append(f"- {task.get('title', 'Untitled task')} [{status}] due {due_date}")
        return "\n".join(lines)

    def _format_notes(self, notes: list[dict[str, Any] | str]) -> str:
        """Format saved note summaries into a readable offline answer."""
        if not notes:
            return "You have no saved local note summaries."

        lines = ["Your saved note summaries:"]
        for note in notes[:3]:
            if isinstance(note, dict):
                lines.append(f"- {note.get('summary') or note.get('title') or 'Untitled note'}")
            else:
                lines.append(f"- {note}")
        return "\n".join(lines)

    def _format_recent_messages(self, messages: list[dict[str, Any]]) -> str:
        """Format recent chat history into a readable memory answer."""
        if not messages:
            return "I do not have any recent chat memory saved yet."

        lines = ["Recent chat memory:"]
        for message in messages[-5:]:
            role = message.get("role", "unknown")
            content = str(message.get("content", "")).strip()
            if content:
                lines.append(f"- {role}: {content}")
        return "\n".join(lines)

    def _format_datetime(self, value: str) -> str:
        """Convert ISO timestamps into a simple human-readable string."""
        if not value:
            return "unknown time"
        try:
            parsed = datetime.fromisoformat(value)
            return parsed.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return value

    def _extract_date_from_message(self, message: str) -> datetime | None:
        """Parse simple month/day date mentions from a user query."""
        match = re.search(
            r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?\b",
            message,
            flags=re.IGNORECASE,
        )
        if not match:
            return None

        month = match.group(1).title()
        day = int(match.group(2))
        for year in (datetime.now().year, datetime.now().year + 1, datetime.now().year - 1):
            try:
                return datetime.strptime(f"{month} {day} {year}", "%B %d %Y")
            except ValueError:
                continue
        return None

    def _event_matches_date(self, value: str, query_date: datetime) -> bool:
        """Check whether an event timestamp falls on the query date."""
        try:
            parsed = datetime.fromisoformat(value)
            return parsed.date() == query_date.date()
        except ValueError:
            return False

    def _event_hour(self, value: str) -> int | None:
        """Extract hour from ISO datetime."""
        try:
            return datetime.fromisoformat(value).hour
        except ValueError:
            return None
