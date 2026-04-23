$ErrorActionPreference = "Stop"

python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

if (Get-Command npm -ErrorAction SilentlyContinue) {
    Push-Location ui
    npm install
    Pop-Location
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "models" | Out-Null

Write-Host "Setup complete. Add your Phi-3 GGUF model under models\\1\\, start MySQL, then run scripts\\run.ps1 or docker compose up --build."
