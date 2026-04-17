"""Local LLM integration via Ollama."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from app.config import get_settings


class LocalLLMEngine:
    """Wrapper for a local Ollama model with deterministic offline fallbacks."""

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
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            response.raise_for_status()
            payload = response.json()
            models = payload.get("models", [])
            return any(model.get("name", "").startswith(self.model_name) for model in models) or bool(models)
        except requests.RequestException:
            return False

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate text locally, falling back to a deterministic local response."""
        payload: dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }
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
            "Provide helpful, concise responses while keeping all data local.\n\n"
        )
        if context:
            prompt += self._build_context_block(context)
        prompt += f"User message:\n{message}\n"
        return self.generate(prompt), "ollama"

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
        return "\n".join(lines) + "\n\n"

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

    def _format_datetime(self, value: str) -> str:
        """Convert ISO timestamps into a simple human-readable string."""
        if not value:
            return "unknown time"
        try:
            parsed = datetime.fromisoformat(value)
            return parsed.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return value
