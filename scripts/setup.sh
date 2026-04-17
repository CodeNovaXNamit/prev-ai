#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if command -v npm >/dev/null 2>&1; then
  (cd ui && npm install)
fi

if [ ! -f .env ]; then
  cp .env.example .env
fi

mkdir -p data models
echo "Setup complete. Start MySQL and Ollama, then run ./scripts/run.sh or docker compose up --build."
