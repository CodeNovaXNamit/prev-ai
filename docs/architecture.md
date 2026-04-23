# Architecture

## Overview

Privacy AI Assistant is a modular offline-first system designed to keep user data on the local device. The application uses encrypted local persistence, a local Phi-3 model runner for language-model inference, a FastAPI backend for service orchestration, and a Next.js frontend for the user experience.

## High-Level Components

```text
+------------------------+
|    Next.js Frontend    |
| chat, tasks, notes UI  |
+-----------+------------+
            |
            v
+------------------------+
|    FastAPI Services    |
| chat, tasks, events,   |
| summaries, health      |
+-----+-----------+------+
      |           |
      v           v
+-----------+  +------------------+
| Phi-3     |  | Encrypted Store  |
| runner    |  | tasks/events/    |
| local LLM |  | notes at rest    |
+-----------+  +------------------+
```

## Modules

### `app/config.py`
Loads environment variables, resolves data paths, and centralizes offline-safe defaults.

### `app/encryption.py`
Uses Fernet for symmetric encryption. A provided passphrase or raw key is normalized into a valid Fernet key using SHA-256.

### `app/database.py`
Implements encrypted persistence for tasks, events, and note summaries. Only encrypted JSON payloads are stored in SQLite.

### `app/task_manager.py`
Contains task CRUD logic. The module is intentionally decoupled from the UI and API layer.

### `app/scheduler.py`
Manages event creation, updates, listing, and deletion for local scheduling.

### `app/summarizer.py`
Uses the local LLM for note summarization when available and falls back to a deterministic extractive summarizer when the model runner is offline.

### `app/llm_engine.py`
Integrates with the model runner at `http://localhost:11435` by default. It never calls cloud APIs and returns a local fallback response if the runner is not reachable.

### `ui/`
Provides the interactive Next.js interface for chatting, managing tasks, scheduling events, and summarizing notes.

## Privacy Model

- All database content is stored locally.
- Payloads are encrypted before hitting disk.
- No external APIs are enabled by default.
- The model runner is expected to run on the same device or Compose network.
- When the model runner is unavailable, the app degrades to local deterministic behavior instead of reaching out to external services.

## Scalability Path

For a production expansion over the next 6-12 months:

1. Add a background job runner for scheduled reminders.
2. Introduce semantic local retrieval with on-device embeddings.
3. Package the UI using a desktop shell such as Tauri or Electron.
4. Add role-based local profiles and hardware-backed key storage.
5. Support GPU-aware model routing between quantized model variants.
