"""Tests for the local LLM wrapper and fallback logic."""

from unittest.mock import Mock, patch

import requests

from app.llm_engine import LocalLLMEngine
from app.summarizer import NotesSummarizer


def test_llm_generate_uses_remote_response_when_available() -> None:
    engine = LocalLLMEngine(model_name="phi3", ollama_url="http://localhost:11434")
    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"response": "Local model reply"}

    with patch("app.llm_engine.requests.post", return_value=fake_response):
        result = engine.generate("Hello")

    assert result == "Local model reply"


def test_llm_generate_falls_back_without_network() -> None:
    engine = LocalLLMEngine(model_name="phi3", ollama_url="http://localhost:11434")

    with patch("app.llm_engine.requests.post", side_effect=requests.RequestException("offline")):
        result = engine.generate("Hello")

    assert "Ollama is not running" in result


def test_chat_answers_schedule_from_local_context_when_ollama_is_offline() -> None:
    engine = LocalLLMEngine(model_name="phi3", ollama_url="http://localhost:11434")
    context = {
        "tasks": [],
        "events": [
            {
                "title": "Advisor meeting",
                "start_time": "2026-04-16T10:00:00",
                "end_time": "2026-04-16T10:30:00",
                "location": "Lab 2",
            }
        ],
        "notes": [],
    }

    with patch.object(engine, "is_available", return_value=False):
        result, source = engine.chat("what is the schedule", context=context)

    assert "Your local schedule:" in result
    assert "Advisor meeting" in result
    assert source == "fallback"


def test_chat_answers_tasks_from_local_context_when_ollama_is_offline() -> None:
    engine = LocalLLMEngine(model_name="phi3", ollama_url="http://localhost:11434")
    context = {
        "tasks": [{"title": "Write report", "completed": False, "due_date": "2026-04-18"}],
        "events": [],
        "notes": [],
    }

    with patch.object(engine, "is_available", return_value=False):
        result, source = engine.chat("show my tasks", context=context)

    assert "Your local tasks:" in result
    assert "Write report" in result
    assert source == "fallback"


def test_summarizer_uses_extractive_fallback(session) -> None:
    engine = LocalLLMEngine()

    summarizer = NotesSummarizer(
        session=session,
        llm_engine=engine,
    )

    with patch.object(engine, "generate", return_value="Local summary fallback: Ollama is unavailable, but the note was processed locally."):
        result = summarizer.summarize(
            title="Research Notes",
            note_text=(
                "Review the privacy paper tomorrow. Finish the benchmark table before Friday. "
                "Test quantized Phi-3 locally on the laptop."
            ),
        )

    assert result["summary"].startswith("- ")
