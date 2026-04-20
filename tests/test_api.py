"""API integration tests for the FastAPI application."""

from __future__ import annotations

from sqlalchemy import text
from unittest.mock import patch


def test_task_event_note_and_analytics_flow(client) -> None:
    task_response = client.post(
        "/tasks",
        json={
            "title": "Finish integration",
            "description": "Connect Next UI to FastAPI",
            "priority": "high",
            "completed": False,
        },
    )
    assert task_response.status_code == 200
    task_id = task_response.json()["id"]

    update_response = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert update_response.status_code == 200
    assert update_response.json()["completed"] is True

    event_response = client.post(
        "/events",
        json={
            "title": "Demo rehearsal",
            "start_time": "2026-04-18T10:00:00",
            "end_time": "2026-04-18T11:00:00",
            "location": "Main hall",
            "notes": "Walk through private workflow",
        },
    )
    assert event_response.status_code == 200

    note_response = client.post(
        "/notes",
        json={"title": "Secure brief", "note_text": "All chats remain local."},
    )
    assert note_response.status_code == 200

    with patch("app.main.llm_engine.generate", return_value="- Capture tasks.\n- Keep data local."):
        summary_response = client.post(
            "/summarize",
            json={"title": "Standup", "note_text": "Capture tasks and keep data local."},
        )
    assert summary_response.status_code == 200
    assert summary_response.json()["summary"].startswith("- ")

    analytics_response = client.get("/analytics")
    assert analytics_response.status_code == 200
    payload = analytics_response.json()
    assert payload["tasks_completed_percent"] == 100
    assert payload["saved_notes"] == 2
    assert payload["scheduled_events"] == 1
    assert payload["sessions"] >= 4


def test_chat_endpoint_uses_fallback_context(client) -> None:
    with patch("app.main.llm_engine.is_available", return_value=False):
        response = client.post("/chat", json={"message": "remember to finish report"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "local-context"
    assert payload["response"] == "I saved this task locally: finish report."
    assert payload["created_tasks"][0]["title"] == "finish report"
    assert payload["created_events"] == []
    tasks_response = client.get("/tasks")
    assert tasks_response.status_code == 200
    assert tasks_response.json()[0]["title"] == "finish report"


def test_chat_can_mark_latest_task_completed(client) -> None:
    created = client.post(
        "/tasks",
        json={"title": "Finish report", "description": "For review", "priority": "medium", "completed": False},
    )
    assert created.status_code == 200

    response = client.post("/chat", json={"message": "this task got completed"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "local-context"
    assert payload["created_tasks"] == []
    assert payload["completed_tasks"][0]["title"] == "Finish report"
    assert "I marked this task as completed" in payload["response"]

    tasks_response = client.get("/tasks")
    assert tasks_response.status_code == 200
    assert tasks_response.json()[0]["completed"] is True


def test_chat_endpoint_saves_meeting_to_schedule(client) -> None:
    response = client.post(
        "/chat",
        json={"message": "I have a meeting on 20th april at 9am in chandigarh"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "local-context"
    assert payload["created_tasks"] == []
    assert payload["created_events"][0]["title"] == "Meeting"
    assert "April 20" in payload["response"]
    assert "09:00 AM" in payload["response"]
    assert "Chandigarh" in payload["response"]

    events_response = client.get("/events")
    assert events_response.status_code == 200
    events = events_response.json()
    assert events[0]["title"] == "Meeting"
    assert events[0]["start_time"].endswith("T09:00:00")
    assert events[0]["location"] == "Chandigarh"


def test_chat_endpoint_saves_meeting_with_at_location_phrase(client) -> None:
    response = client.post(
        "/chat",
        json={"message": "i have a meeting on 20th april at 9 am at location ludhiana"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "local-context"
    assert payload["created_events"][0]["title"] == "Meeting"
    assert "April 20" in payload["response"]
    assert "09:00 AM" in payload["response"]
    assert "Ludhiana" in payload["response"]

    events_response = client.get("/events")
    assert events_response.status_code == 200
    events = events_response.json()
    assert events[0]["location"] == "Ludhiana"


def test_system_status_returns_health_and_test_results(client) -> None:
    response = client.get("/system/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["health"]["app_name"] == "Privacy AI Assistant"
    assert payload["database_connected"] is True
    assert len(payload["latest_test_results"]) >= 1


def test_chat_persists_memory_for_future_use(client) -> None:
    with patch("app.main.llm_engine.is_available", return_value=False):
        first = client.post("/chat", json={"message": "remember that my favorite stack is python"})
        assert first.status_code == 200

        second = client.post("/chat", json={"message": "what do you remember from earlier"})

    assert second.status_code == 200
    payload = second.json()
    assert "Recent chat memory:" in payload["response"]
    assert "my favorite stack is python" in payload["response"]


def test_chat_history_returns_recent_messages(client) -> None:
    response = client.post("/chat", json={"message": "hello there"})
    assert response.status_code == 200

    history = client.get("/chat/history")
    assert history.status_code == 200
    payload = history.json()
    assert any(item["role"] == "user" and "hello there" in item["content"] for item in payload)
    assert any(item["role"] == "assistant" for item in payload)


def test_chat_can_save_and_recall_user_name(client) -> None:
    remember = client.post("/chat", json={"message": "my name is namit greet me"})

    assert remember.status_code == 200
    remember_payload = remember.json()
    assert remember_payload["source"] == "memory"
    assert remember_payload["response"] == "Hello, Namit. I'll remember that."

    recall = client.post("/chat", json={"message": "what is my name"})

    assert recall.status_code == 200
    recall_payload = recall.json()
    assert recall_payload["source"] == "memory"
    assert recall_payload["response"] == "Your name is Namit."


def test_chat_can_save_location_and_list_memories(client) -> None:
    remember = client.post("/chat", json={"message": "I live in Chandigarh"})

    assert remember.status_code == 200
    assert remember.json()["source"] == "memory"

    recall = client.post("/chat", json={"message": "where do i live"})
    assert recall.status_code == 200
    assert "Chandigarh" in recall.json()["response"]

    memories = client.get("/memories")
    assert memories.status_code == 200
    payload = memories.json()
    assert any(item["key"] == "location" and item["value"] == "Chandigarh" for item in payload)


def test_profile_and_project_ground_truth_routes(client) -> None:
    profile = client.post("/profile", json={"attribute": "cgpa", "value": "8.7"})
    assert profile.status_code == 200
    assert profile.json()["attribute"] == "cgpa"

    project = client.post(
        "/projects",
        json={
            "project_id": "HVAC_2025",
            "name": "Smart HVAC",
            "team_members": "Aman, Riya",
            "status": "active",
        },
    )
    assert project.status_code == 200
    assert project.json()["project_id"] == "HVAC_2025"

    profile_list = client.get("/profile")
    assert profile_list.status_code == 200
    assert any(item["attribute"] == "cgpa" and item["value"] == "8.7" for item in profile_list.json())

    project_list = client.get("/projects")
    assert project_list.status_code == 200
    assert any(item["project_id"] == "HVAC_2025" for item in project_list.json())


def test_chat_answers_profile_from_sql_ground_truth(client) -> None:
    client.post("/profile", json={"attribute": "name", "value": "Namit"})

    response = client.post("/chat", json={"message": "what is my name"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "memory"
    assert payload["response"] == "Your name is Namit."


def test_chat_answers_project_from_sql_ground_truth(client) -> None:
    client.post(
        "/projects",
        json={
            "project_id": "FLOOD_2025",
            "name": "Flood Prediction",
            "team_members": "Neha, Arjun",
            "status": "active",
        },
    )

    response = client.post("/chat", json={"message": "tell me about the flood prediction project"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "local-context"
    assert "Flood Prediction [FLOOD_2025] is active." in payload["response"]


def test_chat_does_not_store_assistant_messages_in_chat_history(client, session) -> None:
    response = client.post("/chat", json={"message": "what is my name"})
    assert response.status_code == 200

    count = session.execute(text("SELECT COUNT(*) FROM chat_messages")).scalar_one()
    assert count == 2
