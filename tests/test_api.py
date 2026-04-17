"""API integration tests for the FastAPI application."""

from __future__ import annotations

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
    assert payload["source"] == "fallback"
    assert payload["created_tasks"][0]["title"] == "finish report"
    tasks_response = client.get("/tasks")
    assert tasks_response.status_code == 200
    assert tasks_response.json()[0]["title"] == "finish report"


def test_system_status_returns_health_and_test_results(client) -> None:
    response = client.get("/system/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["health"]["app_name"] == "Privacy AI Assistant"
    assert payload["database_connected"] is True
    assert len(payload["latest_test_results"]) >= 1
