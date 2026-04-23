# API Reference

## Base URL

Local FastAPI server:

```text
http://127.0.0.1:8000
```

## Endpoints

### `GET /health`
Returns application status, database path, and whether the local model runner is reachable.

### `POST /chat`
Request body:

```json
{
  "message": "Summarize my day",
  "context": "Optional local context"
}
```

Response:

```json
{
  "response": "Assistant reply",
  "source": "local-context",
  "created_tasks": [],
  "created_events": []
}
```

### `GET /tasks`
Returns all saved tasks.

### `GET /memories`
Returns all locally remembered user facts such as name, location, and favorites.

### `POST /tasks`
Request body:

```json
{
  "title": "Prepare slides",
  "description": "Focus on the privacy section",
  "due_date": "2026-04-20",
  "priority": "high",
  "completed": false
}
```

### `PUT /tasks/{task_id}`
Updates an existing task with the same payload shape used in `POST /tasks`.

### `DELETE /tasks/{task_id}`
Deletes a task.

### `GET /events`
Returns all stored calendar events.

### `POST /events`
Request body:

```json
{
  "title": "Advisor meeting",
  "start_time": "2026-04-16T10:00:00",
  "end_time": "2026-04-16T10:30:00",
  "location": "Lab 2",
  "notes": "Review benchmark results"
}
```

### `PUT /events/{event_id}`
Updates an event with the same payload shape used in `POST /events`.

### `DELETE /events/{event_id}`
Deletes an event.

### `GET /notes`
Returns stored notes and summaries.

### `POST /summarize`
Request body:

```json
{
  "title": "Lecture notes",
  "note_text": "Long note content..."
}
```

Response includes the note record with its generated summary.
