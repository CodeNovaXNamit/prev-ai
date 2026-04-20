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


def test_local_context_answers_specific_appointment_query() -> None:
    engine = LocalLLMEngine(model_name="phi3", ollama_url="http://localhost:11434")
    context = {
        "tasks": [],
        "events": [
            {
                "title": "Doctor appointment",
                "start_time": "2026-04-20T09:30:00",
                "end_time": "2026-04-20T10:00:00",
                "location": "Clinic",
            },
            {
                "title": "Evening call",
                "start_time": "2026-04-20T18:00:00",
                "end_time": "2026-04-20T18:30:00",
                "location": "Remote",
            },
        ],
        "notes": [],
    }

    result = engine.answer_from_local_context("what appointments do I have on April 20 morning", context)

    assert result is not None
    assert "Doctor appointment" in result
    assert "Evening call" not in result


def test_chat_prompt_filters_unrelated_context_for_general_query() -> None:
    engine = LocalLLMEngine(model_name="phi3", ollama_url="http://localhost:11434")
    context = {
        "tasks": [{"title": "Write report", "completed": False, "due_date": "2026-04-18"}],
        "events": [{"title": "Advisor meeting", "start_time": "2026-04-16T10:00:00", "end_time": "2026-04-16T10:30:00", "location": "Lab 2"}],
        "notes": [{"title": "LM Studio", "summary": "- Some summary"}],
        "recent_messages": [{"role": "user", "content": "my name is namit"}],
        "remembered_facts": [{"key": "location", "value": "Faridabad"}],
    }

    with patch.object(engine, "is_available", return_value=True), patch.object(engine, "generate", return_value="New Delhi") as mocked_generate:
        result, source = engine.chat("capital of India?", context=context)

    assert result == "New Delhi"
    assert source == "ollama"
    prompt = mocked_generate.call_args.args[0]
    assert "Tasks:" not in prompt
    assert "Events:" not in prompt
    assert "Notes:" not in prompt
    assert "Recent chat memory:" not in prompt
    assert "Remembered user facts:" not in prompt


def test_chat_prompt_keeps_history_only_for_history_queries() -> None:
    engine = LocalLLMEngine(model_name="phi3", ollama_url="http://localhost:11434")
    context = {
        "recent_messages": [{"role": "user", "content": "remember that my favorite stack is python"}],
        "remembered_facts": [{"key": "name", "value": "Namit"}],
    }

    with patch.object(engine, "is_available", return_value=True), patch.object(engine, "generate", return_value="Recent chat memory") as mocked_generate:
        engine.chat("what do you remember from earlier", context=context)

    prompt = mocked_generate.call_args.args[0]
    assert "Recent chat memory:" in prompt
    assert "Remembered user facts:" not in prompt


def test_chat_prompt_keeps_project_context_for_project_queries() -> None:
    engine = LocalLLMEngine(model_name="phi3", ollama_url="http://localhost:11434")
    context = {
        "project": {"project_id": "HVAC_2025", "name": "Smart HVAC", "status": "active"},
        "semantic_notes": ["- HVAC note"],
    }

    with patch.object(engine, "is_available", return_value=True), patch.object(engine, "generate", return_value="Project info") as mocked_generate:
        engine.chat("tell me about the smart hvac project", context=context)

    prompt = mocked_generate.call_args.args[0]
    assert "Project:" in prompt
    assert "Semantic notes:" in prompt
