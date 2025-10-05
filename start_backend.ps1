# K-OSMOS Backend Starter for Windows PowerShell
Write-Host "🚀 Starting K-OSMOS Backend API..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check if conda environment is active
if ($env:CONDA_DEFAULT_ENV) {
    Write-Host "✅ Conda environment active: $env:CONDA_DEFAULT_ENV" -ForegroundColor Green
} else {
    Write-Host "⚠️  No conda environment detected. Activating spacey..." -ForegroundColor Yellow
    conda activate spacey
}

# Install requirements
if (Test-Path "requirements.txt") {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    pip install fastapi uvicorn
    Write-Host ""
} else {
    Write-Host "⚠️  requirements.txt not found" -ForegroundColor Yellow
}

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "Please create .env file with required API keys" -ForegroundColor Yellow
    Write-Host "See .env.example for reference" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "🌐 Starting FastAPI server..." -ForegroundColor Green
Write-Host "📍 API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python backend/api_server.py