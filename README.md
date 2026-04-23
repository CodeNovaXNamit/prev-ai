# Privacy AI Assistant

Privacy AI Assistant is a local-first full-stack workspace with a React-based Next.js frontend, a FastAPI backend, MySQL persistence through SQLAlchemy, Fernet encryption for sensitive fields, and a CPU-only Phi-3 model runner for local chat and summarization.

## Stack

- `ui/`: React frontend built with Next.js App Router
- `app/`: FastAPI backend and service layer
- `MySQL + SQLAlchemy`: structured persistence for tasks, events, notes, and behavior analytics
- `Fernet`: encrypted task, note, and schedule content at rest
- `model-runner/python/phi3_runner/`: local Phi-3 GGUF and MiniLM inference service
- `Alembic`: schema migration layer
- `tests/`: API, encryption, ORM, and LLM fallback coverage

## Features

- Simple four-page frontend: home chat, tasks, summaries, dashboard
- Live chat panel connected to the FastAPI backend and local Phi-3 runner
- Tasks captured from chat and stored in MySQL
- Saved summaries page backed by encrypted persisted notes
- Dashboard page for model health, database status, and latest test results
- Dockerized frontend, backend, and MySQL services

## Local Run

### Prerequisites

- Python 3.11+
- Node.js 20+
- MySQL 8+
- Docker and Docker Compose
- A Phi-3 GGUF file in `./models`

### Windows

```powershell
.\scripts\setup.ps1
.\scripts\run.ps1
```

### Linux/macOS

```bash
chmod +x scripts/setup.sh scripts/run.sh
./scripts/setup.sh
./scripts/run.sh
```

Frontend: `http://localhost:3000`

Backend docs: `http://localhost:8000/docs`

Health: `http://localhost:8000/health`

System status: `http://localhost:8000/system/status`

## Docker Run

1. Copy `.env.example` to `.env`.
2. Confirm `MODEL_NAME=phi3`.
3. Place a `Phi-3-mini-4k-instruct` GGUF file in `./models/1/`.
4. Start the stack:

```bash
docker compose up --build -d
```

The backend container calls the `phi3-runner` service over Docker Compose networking using `MODEL_RUNNER_URL=http://phi3-runner:8080`. The runner loads the GGUF file from the mounted `./models` volume.

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
- If the model runner is unavailable, chat and summary flows fall back locally rather than sending data to a cloud service.

## License

MIT. See [LICENSE](LICENSE).
