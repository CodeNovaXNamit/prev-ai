"""Tests for the local LLM wrapper and fallback logic."""

from unittest.mock import Mock, patch

import requests

from app.llm_engine import LocalLLMEngine
from app.semantic_memory import _build_note_query_filter, SemanticMemoryService
from app.summarizer import NotesSummarizer


def test_llm_generate_uses_remote_response_when_available() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")
    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"text": "Local model reply"}

    with patch("app.llm_engine.requests.post", return_value=fake_response):
        result = engine.generate("Hello")

    assert result == "Local model reply"


def test_llm_generate_reads_openai_style_response_content() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")
    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "OpenAI-style reply",
                }
            }
        ]
    }

    with patch("app.llm_engine.requests.post", return_value=fake_response):
        result = engine.generate("Hello")

    assert result == "OpenAI-style reply"


def test_llm_generate_allows_call_specific_options() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")
    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"text": "Configured reply"}

    with patch("app.llm_engine.requests.post", return_value=fake_response) as mocked_post:
        result = engine.generate("Hello", options={"temperature": 0.0, "num_predict": 80})

    assert result == "Configured reply"
    payload = mocked_post.call_args.kwargs["json"]
    assert payload["temperature"] == 0.0
    assert payload["max_tokens"] == 80
    assert "Primary Location: Nilokheri, Haryana, India." in payload["prompt"]
    assert "Never assume the user is in Thailand" in payload["prompt"]


def test_extraction_prompt_does_not_include_static_grounding() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")

    prompt = engine.get_extraction_prompt("my name is namit and i study at siet")

    assert "USER_INPUT: my name is namit and i study at siet" in prompt
    assert "Nilokheri" not in prompt
    assert "Thailand" not in prompt


def test_llm_generate_falls_back_without_network() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")

    with patch("app.llm_engine.requests.post", side_effect=requests.RequestException("offline")):
        result = engine.generate("Hello")

    assert "model runner is unavailable" in result


def test_llm_is_available_accepts_normalized_model_aliases() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")
    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {
        "status": "ok",
        "active_model": "Phi-3-mini-4k-instruct-q4.gguf",
    }

    with patch("app.llm_engine.requests.get", return_value=fake_response):
        assert engine.is_available() is True


def test_chat_answers_schedule_from_local_context_when_runner_is_offline() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")
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


def test_chat_falls_back_when_runner_returns_empty_text() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")
    context = {
        "tasks": [],
        "events": [],
        "notes": [],
        "recent_messages": [],
        "profile_data": {},
        "dynamic_facts": [],
    }
    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"text": "   "}

    with patch.object(engine, "is_available", return_value=True), patch(
        "app.llm_engine.requests.post", return_value=fake_response
    ):
        result, source = engine.chat("what is photoshynthesis", context=context)

    assert "full free-form chat is unavailable" in result
    assert source == "fallback"


def test_chat_answers_tasks_from_local_context_when_runner_is_offline() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")
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


def test_local_context_answers_simple_greeting_without_profile_echo() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")

    result = engine.answer_from_local_context("hi", {"profile_data": {"name": "Namit", "location": "Nilokheri"}})

    assert result == "Hello. How can I help?"


def test_summarizer_uses_extractive_fallback(session) -> None:
    engine = LocalLLMEngine()

    summarizer = NotesSummarizer(
        session=session,
        llm_engine=engine,
    )

    with patch.object(engine, "generate", return_value="Local summary fallback: the model runner is unavailable, but the note was processed locally."):
        result = summarizer.summarize(
            title="Research Notes",
            note_text=(
                "Review the privacy paper tomorrow. Finish the benchmark table before Friday. "
                "Test quantized Phi-3 locally on the laptop."
            ),
        )

    assert result["summary"].startswith("- ")


def test_summarizer_rejects_unrelated_tool_like_output(session) -> None:
    engine = LocalLLMEngine()
    summarizer = NotesSummarizer(session=session, llm_engine=engine)

    bad_output = (
        "- Ensure `.pytest_tmp/` directory isn't in use.\n"
        "- Terminate the process and run git pull.\n"
        "- Use rm -rf cautiously."
    )

    with patch.object(engine, "generate", return_value=bad_output):
        result = summarizer.summarize(
            title="Lecture Notes",
            note_text="Consensus improves resilience. Leader election coordinates writes. Failure detection matters.",
        )

    assert ".pytest_tmp" not in result["summary"]
    assert "Leader election" in result["summary"] or "Consensus" in result["summary"]


def test_summarizer_uses_stricter_generation_options(session) -> None:
    engine = LocalLLMEngine()
    summarizer = NotesSummarizer(session=session, llm_engine=engine)

    with patch.object(engine, "generate", side_effect=["- Chunk summary", "- Final summary"]) as mocked_generate:
        summarizer.summarize(
            title="Lecture Notes",
            note_text="Consensus improves resilience. Leader election coordinates writes. Failure detection matters.",
        )

    first_call = mocked_generate.call_args_list[0]
    second_call = mocked_generate.call_args_list[-1]
    assert first_call.kwargs["options"]["temperature"] == 0.0
    assert first_call.kwargs["options"]["num_predict"] == 100
    assert second_call.kwargs["options"]["num_predict"] == 160
    assert second_call.kwargs["options"]["repeat_penalty"] == 1.15


def test_local_context_answers_specific_appointment_query() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")
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
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")
    context = {
        "tasks": [{"title": "Write report", "completed": False, "due_date": "2026-04-18"}],
        "events": [{"title": "Advisor meeting", "start_time": "2026-04-16T10:00:00", "end_time": "2026-04-16T10:30:00", "location": "Lab 2"}],
        "notes": [{"title": "LM Studio", "summary": "- Some summary"}],
        "recent_messages": [{"role": "user", "content": "my name is namit"}],
        "profile_data": {"name": "Namit", "location": "Faridabad"},
        "dynamic_facts": [{"text": "The user is from Faridabad.", "importance": 4}],
    }

    with patch.object(engine, "is_available", return_value=True), patch.object(
        engine, "_request_generation", return_value="New Delhi"
    ) as mocked_request:
        result, source = engine.chat("capital of India?", context=context)

    assert result == "New Delhi"
    assert source == "model-runner"
    prompt = mocked_request.call_args.args[0]["prompt"]
    assert "Tasks:" not in prompt
    assert "Events:" not in prompt
    assert "Notes:" not in prompt
    assert "### RECENT CONVERSATION" in prompt
    assert "### IDENTITY" in prompt
    assert "### STATIC GROUNDING (Source of Truth)" in prompt
    assert "Faridabad" in prompt


def test_chat_prompt_omits_empty_memory_and_history_sections() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")

    with patch.object(engine, "is_available", return_value=True), patch.object(
        engine, "_request_generation", return_value="Hello"
    ) as mocked_request:
        engine.chat("hello", context={"profile_data": {}})

    prompt = mocked_request.call_args.args[0]["prompt"]
    assert "### RELEVANT MEMORIES" not in prompt
    assert "### RECENT CONVERSATION" not in prompt


def test_chat_prompt_keeps_history_only_for_history_queries() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")
    context = {
        "recent_messages": [{"role": "user", "content": "remember that my favorite stack is python"}],
        "profile_data": {"name": "Namit"},
        "dynamic_facts": [{"text": "The user's favorite stack is Python.", "importance": 3}],
    }

    with patch.object(engine, "is_available", return_value=True), patch.object(
        engine, "_request_generation", return_value="Recent chat memory"
    ) as mocked_request:
        engine.chat("what do you remember from earlier", context=context)

    prompt = mocked_request.call_args.args[0]["prompt"]
    assert "### RECENT CONVERSATION" in prompt
    assert "favorite stack is Python" in prompt


def test_chat_prompt_keeps_project_context_for_project_queries() -> None:
    engine = LocalLLMEngine(model_name="phi3", model_runner_url="http://localhost:11435")
    context = {
        "project": {"project_id": "HVAC_2025", "name": "Smart HVAC", "status": "active"},
        "semantic_notes": ["- HVAC note"],
    }

    with patch.object(engine, "is_available", return_value=True), patch.object(
        engine, "_request_generation", return_value="Project info"
    ) as mocked_request:
        engine.chat("tell me about the smart hvac project", context=context)

    prompt = mocked_request.call_args.args[0]["prompt"]
    assert "### PROJECT CONTEXT" in prompt
    assert "### RELATED NOTES" in prompt


def test_summarizer_discards_noisy_chunks_before_master_summary(session) -> None:
    engine = LocalLLMEngine()
    summarizer = NotesSummarizer(session=session, llm_engine=engine)
    noisy = "\n".join(
        [
            "FOO=bar",
            "BAR=baz",
            "HELLO=world",
            "PATH=/tmp",
            "HOME=/tmp",
            "TOKEN=abc",
        ]
    )
    clean = "Privacy preserving AI can run locally on a laptop. Students can review notes and tasks offline."

    with patch.object(engine, "generate", side_effect=["- Clean chunk", "- Final summary"]) as mocked_generate:
        summarizer.summarize(title="Mixed", note_text=f"{clean}\n\n{noisy}")

    first_prompt = mocked_generate.call_args_list[0].args[0]
    assert "Privacy preserving AI" in first_prompt
    assert "TOKEN=abc" not in first_prompt


def test_build_note_query_filter_uses_and_operator_for_project_scope() -> None:
    assert _build_note_query_filter(None) == {"kind": "note"}
    assert _build_note_query_filter("FLOOD_2025") == {
        "$and": [
            {"kind": "note"},
            {"project_id": "FLOOD_2025"},
        ]
    }


def test_semantic_memory_query_uses_chroma_compatible_filter() -> None:
    collection = Mock()
    collection.query.return_value = {"documents": [["Project note"]]}
    model = Mock()
    embedding = Mock()
    embedding.tolist.return_value = [0.1, 0.2, 0.3]
    model.encode.return_value = [embedding]

    with (
        patch("app.semantic_memory._get_collection", return_value=collection),
        patch("app.semantic_memory._load_embedding_model", return_value=model),
    ):
        result = SemanticMemoryService().query_notes("flood prediction", project_id="FLOOD_2025")

    assert result == ["Project note"]
    assert collection.query.call_args.kwargs["where"] == {
        "$and": [
            {"kind": "note"},
            {"project_id": "FLOOD_2025"},
        ]
    }
