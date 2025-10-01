# K-OSMOS Space Biology Knowledge Engine Launcher
# Quick start script for Windows PowerShell

Write-Host "🚀 K-OSMOS Space Biology Knowledge Engine" -ForegroundColor Green
Write-Host "NASA Space Apps Challenge 2025" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+ first." -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️  No virtual environment found. Installing dependencies globally." -ForegroundColor Yellow
}

# Install dependencies if requirements.txt exists
if (Test-Path "requirements.txt") {
    Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
} else {
    Write-Host "⚠️  requirements.txt not found." -ForegroundColor Yellow
}

# Check environment variables
Write-Host "`n🔍 Checking environment..." -ForegroundColor Cyan

if ($env:GEMINI_API_KEY) {
    Write-Host "✅ GEMINI_API_KEY is set" -ForegroundColor Green
} else {
    Write-Host "❌ GEMINI_API_KEY not found" -ForegroundColor Red
    Write-Host "   Set it with: `$env:GEMINI_API_KEY='your-key-here'" -ForegroundColor Yellow
}

if ($env:PINECONE_API_KEY) {
    Write-Host "✅ PINECONE_API_KEY is set" -ForegroundColor Green
} else {
    Write-Host "❌ PINECONE_API_KEY not found" -ForegroundColor Red
    Write-Host "   Set it with: `$env:PINECONE_API_KEY='your-key-here'" -ForegroundColor Yellow
}

# Offer to run tests
Write-Host "`n🧪 Would you like to run API tests first? (y/n)" -ForegroundColor Cyan
$testChoice = Read-Host

if ($testChoice -eq "y" -or $testChoice -eq "Y") {
    Write-Host "Running API tests..." -ForegroundColor Yellow
    python test_apis.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Tests failed. Please fix the issues before proceeding." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "`nPress Enter to continue..." -ForegroundColor Yellow
    Read-Host
}

# Launch options
Write-Host "`n🚀 Choose launch option:" -ForegroundColor Cyan
Write-Host "1. Launch K-OSMOS Dashboard (Recommended)"
Write-Host "2. Initialize system first"
Write-Host "3. Run tests only"
Write-Host "4. Exit"

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n🌟 Starting K-OSMOS Dashboard..." -ForegroundColor Green
        Write-Host "Access at: http://localhost:8501" -ForegroundColor Cyan
        python -m streamlit run kosmos_app.py
    }
    "2" {
        Write-Host "`n⚙️  Initializing system..." -ForegroundColor Yellow
        python main.py init
        
        Write-Host "`n🌟 Now starting dashboard..." -ForegroundColor Green
        python -m streamlit run kosmos_app.py
    }
    "3" {
        Write-Host "`n🧪 Running tests..." -ForegroundColor Yellow
        python test_apis.py
    }
    "4" {
        Write-Host "👋 Goodbye!" -ForegroundColor Green
        exit 0
    }
    default {
        Write-Host "❌ Invalid choice. Starting dashboard..." -ForegroundColor Yellow
        python -m streamlit run kosmos_app.py
    }
}