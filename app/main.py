"""FastAPI entrypoint for the privacy-first assistant."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.analytics import AnalyticsService
from app.chat_memory import ChatMemoryService
from app.config import (
    AnalyticsResponse,
    ChatRequest,
    ChatResponse,
    EventBase,
    EventUpdate,
    HealthStatus,
    NoteCreate,
    ProfileFact,
    ProjectRegistryEntry,
    SummaryRequest,
    SystemStatusResponse,
    TaskBase,
    TaskUpdate,
    get_settings,
)
from app.database import get_db, init_database
from app.ground_truth_service import GroundTruthService
from app.llm_engine import LocalLLMEngine
from app.memory_service import UserMemoryService
from app.router_service import IntentRouterService
from app.scheduler import SchedulerManager
from app.semantic_memory import SemanticMemoryService
from app.summarizer import NotesSummarizer
from app.system_status import SystemStatusService
from app.task_manager import TaskManager


settings = get_settings()
llm_engine = LocalLLMEngine()
intent_router = IntentRouterService()


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    """Initialize shared resources when the API starts."""
    init_database()
    yield


def create_app() -> FastAPI:
    """Create the FastAPI application with runtime configuration."""
    app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=app_lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()
DbSession = Annotated[Session, Depends(get_db)]


def get_task_manager(session: DbSession) -> TaskManager:
    return TaskManager(session)


def get_scheduler_manager(session: DbSession) -> SchedulerManager:
    return SchedulerManager(session)


def get_notes_service(session: DbSession) -> NotesSummarizer:
    return NotesSummarizer(session, llm_engine, semantic_memory=SemanticMemoryService())


def get_analytics_service(session: DbSession) -> AnalyticsService:
    return AnalyticsService(session)


def get_chat_memory_service(session: DbSession) -> ChatMemoryService:
    return ChatMemoryService(session, semantic_memory=SemanticMemoryService())


def get_user_memory_service(session: DbSession) -> UserMemoryService:
    return UserMemoryService(session)


def get_ground_truth_service(session: DbSession) -> GroundTruthService:
    return GroundTruthService(session)


def get_system_status_service(session: DbSession) -> SystemStatusService:
    return SystemStatusService(session, llm_engine)


def _build_capture_response(
    created_tasks: list[dict[str, Any]],
    created_events: list[dict[str, Any]],
    completed_tasks: list[dict[str, Any]],
) -> str | None:
    """Return a same-turn confirmation for locally captured tasks or events."""
    if completed_tasks:
        titles = ", ".join(task["title"] for task in completed_tasks[:3])
        return f"I marked this task as completed: {titles}."

    if created_events:
        event = created_events[0]
        start = event.get("start_time", "")
        try:
            formatted = f"{datetime.fromisoformat(start):%B %d, %Y at %I:%M %p}"
        except ValueError:
            formatted = start
        location = event.get("location") or "No location"
        return f"I saved your event locally: {event['title']} on {formatted} in {location}."

    if created_tasks:
        titles = ", ".join(task["title"] for task in created_tasks[:3])
        return f"I saved this task locally: {titles}."

    return None


@app.get("/health", response_model=HealthStatus)
def health_check() -> HealthStatus:
    """Return application health information."""
    return HealthStatus(
        app_name=settings.app_name,
        offline_mode=not settings.allow_external_network,
        ollama_available=llm_engine.is_available(),
        database_url=settings.database_url,
        active_model=settings.model_name,
    )


@app.get("/")
def root() -> dict[str, str]:
    """Provide a simple root response for browser hits and container checks."""
    return {
        "message": "PrevAI backend is running.",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    tasks: Annotated[TaskManager, Depends(get_task_manager)],
    scheduler: Annotated[SchedulerManager, Depends(get_scheduler_manager)],
    notes: Annotated[NotesSummarizer, Depends(get_notes_service)],
    memory: Annotated[ChatMemoryService, Depends(get_chat_memory_service)],
    user_memory: Annotated[UserMemoryService, Depends(get_user_memory_service)],
    ground_truth: Annotated[GroundTruthService, Depends(get_ground_truth_service)],
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> ChatResponse:
    """Return an assistant response."""
    memory.add_message("user", request.message)
    profile_answer = ground_truth.answer_profile_query(request.message)
    if profile_answer is not None:
        analytics.track("chat", "memory_recalled", {"kind": "profile_sql"})
        return ChatResponse(
            response=profile_answer,
            source="memory",
            created_tasks=[],
            created_events=[],
            completed_tasks=[],
        )

    recalled_answer = user_memory.answer_memory_query(request.message)
    if recalled_answer is not None:
        analytics.track("chat", "memory_recalled", {"kind": "fact"})
        return ChatResponse(
            response=recalled_answer,
            source="memory",
            created_tasks=[],
            created_events=[],
            completed_tasks=[],
        )

    captured_memories = user_memory.capture_memories_from_message(request.message)
    ground_truth.sync_profile_memories(captured_memories)
    created_tasks = tasks.create_tasks_from_message(request.message)
    completed_tasks = tasks.complete_tasks_from_message(request.message)
    created_events = scheduler.create_events_from_message(request.message)
    intent = intent_router.classify(request.message)
    project = ground_truth.resolve_project(request.message)
    semantic_notes = []
    if intent in {"PROJECT_INFO", "NOTE"}:
        semantic_notes = SemanticMemoryService().query_notes(
            request.message,
            project_id=project["project_id"] if project else None,
        )
    context = {
        "tasks": tasks.list_tasks()[:5],
        "events": scheduler.list_events()[:5],
        "notes": notes.list_notes()[:5],
        "recent_messages": memory.list_recent_messages(limit=8),
        "remembered_facts": ground_truth.list_profile()[:5],
        "semantic_notes": semantic_notes,
        "project": project,
        "intent": intent,
    }
    local_context_answer = llm_engine.answer_from_local_context(request.message, context)
    if captured_memories:
        response = user_memory.build_capture_response(request.message, captured_memories) or ""
        source = "memory"
    elif created_tasks or created_events or completed_tasks:
        response = _build_capture_response(created_tasks, created_events, completed_tasks) or ""
        source = "local-context"
    elif local_context_answer is not None:
        response = local_context_answer
        source = "local-context"
    elif intent == "PROJECT_INFO":
        project_answer = ground_truth.answer_project_query(request.message)
        if project_answer is not None:
            response = project_answer
            if semantic_notes:
                response += "\nRelated project notes:\n" + "\n".join(f"- {item}" for item in semantic_notes[:3])
            source = "local-context"
        else:
            response, source = llm_engine.chat(request.message, context={"project": project, "semantic_notes": semantic_notes, "intent": intent})
    elif intent == "GENERAL":
        response, source = llm_engine.chat(request.message, context={"intent": intent})
    else:
        response, source = llm_engine.chat(request.message, context=context)
    analytics.track("chat", "message_sent", {"source": source})
    for task in created_tasks:
        analytics.track("tasks", "task_created_from_chat", {"task_id": task["id"]})
    for task in completed_tasks:
        analytics.track("tasks", "task_completed_from_chat", {"task_id": task["id"]})
    for event in created_events:
        analytics.track("schedule", "event_created_from_chat", {"event_id": event["id"]})
    for item in captured_memories:
        analytics.track("chat", "memory_saved", {"key": item["key"]})
    return ChatResponse(
        response=response,
        source=source,
        created_tasks=[{"id": task["id"], "title": task["title"]} for task in created_tasks],
        created_events=[{"id": event["id"], "title": event["title"]} for event in created_events],
        completed_tasks=[{"id": task["id"], "title": task["title"]} for task in completed_tasks],
    )


@app.get("/memories")
def list_memories(
    user_memory: Annotated[UserMemoryService, Depends(get_user_memory_service)],
) -> list[dict[str, str]]:
    """List saved personal facts remembered locally for the user."""
    return user_memory.list_memories()


@app.get("/profile")
def list_profile(
    ground_truth: Annotated[GroundTruthService, Depends(get_ground_truth_service)],
) -> list[dict[str, str]]:
    """List structured profile facts."""
    return ground_truth.list_profile()


@app.post("/profile")
def upsert_profile(
    request: ProfileFact,
    ground_truth: Annotated[GroundTruthService, Depends(get_ground_truth_service)],
) -> dict[str, str]:
    """Insert or update one structured profile fact."""
    return ground_truth.upsert_profile(request.attribute, request.value)


@app.get("/projects")
def list_projects(
    ground_truth: Annotated[GroundTruthService, Depends(get_ground_truth_service)],
) -> list[dict[str, str]]:
    """List the project registry."""
    return ground_truth.list_projects()


@app.post("/projects")
def upsert_project(
    request: ProjectRegistryEntry,
    ground_truth: Annotated[GroundTruthService, Depends(get_ground_truth_service)],
) -> dict[str, str]:
    """Insert or update a project registry entry."""
    return ground_truth.upsert_project(
        request.project_id,
        request.name,
        team_members=request.team_members,
        status=request.status,
    )


@app.get("/tasks")
def list_tasks(tasks: Annotated[TaskManager, Depends(get_task_manager)]) -> list[dict[str, Any]]:
    """List tasks."""
    return tasks.list_tasks()


@app.post("/tasks")
def create_task(
    request: TaskBase,
    tasks: Annotated[TaskManager, Depends(get_task_manager)],
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> dict[str, Any]:
    """Create a task."""
    created = tasks.add_task(**request.model_dump())
    analytics.track("tasks", "task_created", {"priority": created["priority"]})
    return created


@app.patch("/tasks/{task_id}")
@app.put("/tasks/{task_id}")
def update_task(
    task_id: str,
    request: TaskUpdate,
    tasks: Annotated[TaskManager, Depends(get_task_manager)],
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> dict[str, Any]:
    """Update a task."""
    try:
        updated = tasks.update_task(task_id, **request.model_dump(exclude_unset=True))
        analytics.track("tasks", "task_updated", {"task_id": task_id})
        return updated
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: str,
    tasks: Annotated[TaskManager, Depends(get_task_manager)],
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> dict[str, bool]:
    """Delete a task."""
    deleted = tasks.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found.")
    analytics.track("tasks", "task_deleted", {"task_id": task_id})
    return {"deleted": True}


@app.get("/events")
def list_events(
    scheduler: Annotated[SchedulerManager, Depends(get_scheduler_manager)],
) -> list[dict[str, Any]]:
    """List events."""
    return scheduler.list_events()


@app.post("/events")
def create_event(
    request: EventBase,
    scheduler: Annotated[SchedulerManager, Depends(get_scheduler_manager)],
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> dict[str, Any]:
    """Create an event."""
    created = scheduler.add_event(**request.model_dump())
    analytics.track("schedule", "event_created", {"event_id": created["id"]})
    return created


@app.patch("/events/{event_id}")
@app.put("/events/{event_id}")
def update_event(
    event_id: str,
    request: EventUpdate,
    scheduler: Annotated[SchedulerManager, Depends(get_scheduler_manager)],
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> dict[str, Any]:
    """Update an event."""
    try:
        updated = scheduler.update_event(event_id, **request.model_dump(exclude_unset=True))
        analytics.track("schedule", "event_updated", {"event_id": event_id})
        return updated
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/events/{event_id}")
def delete_event(
    event_id: str,
    scheduler: Annotated[SchedulerManager, Depends(get_scheduler_manager)],
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> dict[str, bool]:
    """Delete an event."""
    deleted = scheduler.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found.")
    analytics.track("schedule", "event_deleted", {"event_id": event_id})
    return {"deleted": True}


@app.get("/notes")
def list_notes(
    notes: Annotated[NotesSummarizer, Depends(get_notes_service)],
) -> list[dict[str, Any]]:
    """List stored notes."""
    return notes.list_notes()


@app.get("/summaries")
def list_summaries(
    notes: Annotated[NotesSummarizer, Depends(get_notes_service)],
) -> list[dict[str, Any]]:
    """List only notes with generated summaries."""
    return [note for note in notes.list_notes() if note.get("summary")]


@app.post("/notes")
def create_note(
    request: NoteCreate,
    notes: Annotated[NotesSummarizer, Depends(get_notes_service)],
    ground_truth: Annotated[GroundTruthService, Depends(get_ground_truth_service)],
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> dict[str, Any]:
    """Create a note without summary generation."""
    project = ground_truth.resolve_project(f"{request.title}\n{request.note_text}")
    payload = request.model_dump()
    payload["project_id"] = payload.get("project_id") or (project["project_id"] if project else None)
    created = notes.create_note(**payload)
    analytics.track("notes", "note_created", {"note_id": created["id"]})
    return created


@app.delete("/notes/{note_id}")
def delete_note(
    note_id: str,
    notes: Annotated[NotesSummarizer, Depends(get_notes_service)],
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> dict[str, bool]:
    """Delete a note."""
    deleted = notes.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found.")
    analytics.track("notes", "note_deleted", {"note_id": note_id})
    return {"deleted": True}


@app.post("/summarize")
def summarize_note(
    request: SummaryRequest,
    notes: Annotated[NotesSummarizer, Depends(get_notes_service)],
    ground_truth: Annotated[GroundTruthService, Depends(get_ground_truth_service)],
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> dict[str, Any]:
    """Summarize and store a note."""
    project = ground_truth.resolve_project(f"{request.title}\n{request.note_text}")
    record = notes.summarize(
        request.title,
        request.note_text,
        project_id=request.project_id or (project["project_id"] if project else None),
    )
    analytics.track("summarizer", "summary_generated", {"note_id": record["id"]})
    return record


@app.get("/analytics", response_model=AnalyticsResponse)
def analytics_dashboard(
    tasks: Annotated[TaskManager, Depends(get_task_manager)],
    scheduler: Annotated[SchedulerManager, Depends(get_scheduler_manager)],
    notes: Annotated[NotesSummarizer, Depends(get_notes_service)],
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> AnalyticsResponse:
    """Return dashboard metrics derived from stored behavior and data."""
    payload = analytics.build_dashboard(
        tasks=tasks.list_tasks(),
        events=scheduler.list_events(),
        notes=notes.list_notes(),
    )
    return AnalyticsResponse(**payload)


@app.get("/system/status", response_model=SystemStatusResponse)
def system_status(
    tasks: Annotated[TaskManager, Depends(get_task_manager)],
    scheduler: Annotated[SchedulerManager, Depends(get_scheduler_manager)],
    notes: Annotated[NotesSummarizer, Depends(get_notes_service)],
    system: Annotated[SystemStatusService, Depends(get_system_status_service)],
) -> SystemStatusResponse:
    """Return model, database, and verification status for the dashboard page."""
    summaries = [note for note in notes.list_notes() if note.get("summary")]
    return system.build_status(
        task_count=len(tasks.list_tasks()),
        summary_count=len(summaries),
        event_count=len(scheduler.list_events()),
    )
