# Privacy AI Assistant

Privacy AI Assistant is a local-first full-stack workspace with a React-based Next.js frontend, a FastAPI backend, MySQL persistence through SQLAlchemy, Fernet encryption for sensitive fields, and Ollama-backed chat and summarization using your local `phi3` model.

## Stack

- `ui/`: React frontend built with Next.js App Router
- `app/`: FastAPI backend and service layer
- `MySQL + SQLAlchemy`: structured persistence for tasks, events, notes, and behavior analytics
- `Fernet`: encrypted task, note, and schedule content at rest
- `Ollama`: local inference endpoint for chat and note summarization
- `Alembic`: schema migration layer
- `tests/`: API, encryption, ORM, and LLM fallback coverage

## Features

- Simple four-page frontend: home chat, tasks, summaries, dashboard
- Live chat panel connected to the FastAPI backend and Ollama
- Tasks captured from chat and stored in MySQL
- Saved summaries page backed by encrypted persisted notes
- Dashboard page for model health, database status, and latest test results
- Dockerized frontend, backend, and MySQL services

## Local Run

### Prerequisites

- Python 3.11+
- Node.js 20+
- MySQL 8+
- Ollama installed locally with `phi3`

### Windows

```powershell
.\scripts\setup.ps1
ollama list
.\scripts\run.ps1
```

### Linux/macOS

```bash
chmod +x scripts/setup.sh scripts/run.sh
./scripts/setup.sh
ollama list
./scripts/run.sh
```

Frontend: `http://localhost:3000`

Backend docs: `http://localhost:8000/docs`

Health: `http://localhost:8000/health`

System status: `http://localhost:8000/system/status`

## Docker Run

1. Copy `.env.example` to `.env`.
2. Confirm `MODEL_NAME=phi3`.
3. Keep Ollama running on the host machine.
4. Start the stack:

```bash
docker compose up --build -d
```

The backend container uses `http://host.docker.internal:11434` to reach host Ollama. On Windows this works as-is. On Linux, Docker Compose adds `host-gateway`; if your Docker version is older, update Docker or override `OLLAMA_URL`.

Do not commit `.env` to GitHub. Keep secrets and your generated Fernet key only in local environment files or GitHub secrets.

## Database And Migrations

- Default local database URL: `mysql+pymysql://prevai:prevai@localhost:3306/prevai`
- Run migrations manually with:

```bash
alembic upgrade head
```

## Tests

```bash
pytest
```

The test suite uses an isolated SQLite database for speed while keeping the same SQLAlchemy models and encrypted field behavior as production.

## Privacy Notes

- Sensitive task titles, descriptions, note bodies, summaries, event titles, locations, and notes are encrypted before persistence.
- The UI never talks directly to the database.
- If Ollama is unavailable, chat and summary flows fall back locally rather than sending data to a cloud service.

## License

MIT. See [LICENSE](LICENSE).
