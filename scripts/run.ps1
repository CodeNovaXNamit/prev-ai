$ErrorActionPreference = "Stop"

. .\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = (Get-Location).Path

Start-Process powershell -ArgumentList "-NoExit", "-Command", ". .\\.venv\\Scripts\\Activate.ps1; Set-Location '$((Get-Location).Path)'; `$env:PYTHONPATH='$((Get-Location).Path)'; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$((Join-Path (Get-Location).Path 'ui'))'; npm run dev -- --hostname 0.0.0.0 --port 3000"

Write-Host "Backend starting at http://localhost:8000 and frontend at http://localhost:3000"
Write-Host "Make sure the Docker Phi-3 runner is available for containerized runs, or set MODEL_RUNNER_URL in .env for your local runner."
