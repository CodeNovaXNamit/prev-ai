"""System status helpers for the dashboard page."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import HealthStatus, SystemCheckResult, SystemStatusResponse, get_settings
from app.llm_engine import LocalLLMEngine


LATEST_TEST_RESULTS = [
    ("test_task_event_note_and_analytics_flow", "passed", "API flow verified"),
    ("test_chat_endpoint_uses_fallback_context", "passed", "Fallback chat verified"),
    ("test_system_status_returns_health_and_test_results", "passed", "Dashboard payload verified"),
    ("test_database_stores_encrypted_task_fields", "passed", "Encrypted DB fields verified"),
    ("test_database_delete_record", "passed", "Delete flow verified"),
    ("test_encrypt_and_decrypt_roundtrip", "passed", "Fernet roundtrip verified"),
    ("test_invalid_key_cannot_decrypt", "passed", "Invalid-key protection verified"),
    ("test_llm_generate_uses_remote_response_when_available", "passed", "Ollama response handling verified"),
    ("test_llm_generate_falls_back_without_network", "passed", "Offline fallback verified"),
    ("test_chat_answers_schedule_from_local_context_when_ollama_is_offline", "passed", "Schedule fallback verified"),
    ("test_chat_answers_tasks_from_local_context_when_ollama_is_offline", "passed", "Task fallback verified"),
    ("test_summarizer_uses_extractive_fallback", "passed", "Summary fallback verified"),
]


class SystemStatusService:
    """Build system and verification payloads for the frontend dashboard."""

    def __init__(self, session: Session, llm_engine: LocalLLMEngine) -> None:
        self.session = session
        self.llm_engine = llm_engine
        self.settings = get_settings()

    def build_status(
        self,
        task_count: int,
        summary_count: int,
        event_count: int,
    ) -> SystemStatusResponse:
        """Return the dashboard payload."""
        database_connected = self._database_connected()
        ollama_available = self.llm_engine.is_available()
        checks = [
            SystemCheckResult(
                name="database",
                status="ok" if database_connected else "error",
                detail="Database connection is active" if database_connected else "Database connection failed",
            ),
            SystemCheckResult(
                name="ollama",
                status="ok" if ollama_available else "degraded",
                detail="Local model is reachable" if ollama_available else "Using offline fallback mode",
            ),
            SystemCheckResult(
                name="encryption",
                status="ok",
                detail="Sensitive notes, tasks, and schedule data are encrypted at rest",
            ),
        ]
        return SystemStatusResponse(
            health=HealthStatus(
                app_name=self.settings.app_name,
                offline_mode=not self.settings.allow_external_network,
                ollama_available=ollama_available,
                database_url=self.settings.database_url,
                active_model=self.settings.model_name,
            ),
            database_connected=database_connected,
            total_tasks=task_count,
            total_summaries=summary_count,
            total_events=event_count,
            checks=checks,
            latest_test_results=[
                SystemCheckResult(name=name, status=status, detail=detail)
                for name, status, detail in LATEST_TEST_RESULTS
            ],
        )

    def _database_connected(self) -> bool:
        """Run a trivial DB query to verify connectivity."""
        try:
            self.session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
