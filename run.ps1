$ErrorActionPreference = 'Stop'

Write-Host "Legal Guidance AI Chatbot - Stage 1A" -ForegroundColor Cyan

if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Green
    python -m venv venv
}

& ".\venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\venv\Scripts\python.exe" -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example. Set SECRET_KEY before starting the app." -ForegroundColor Yellow
    exit 1
}

if (Test-Path "signup.db") {
    Write-Host "Existing signup.db found. Running the one-time migration..." -ForegroundColor Yellow
    & ".\venv\Scripts\python.exe" migrate_db.py
}

Write-Host "Starting Flask application..." -ForegroundColor Green
& ".\venv\Scripts\python.exe" app.py
