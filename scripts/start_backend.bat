@echo off
echo 🔧 Starting K-OSMOS Backend Server...

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  No .env file found. Please copy .env.example to .env and configure your API keys.
    echo 📋 Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Please edit .env file and add your API keys before running again.
    pause
    exit /b 1
)

echo 🚀 Starting FastAPI server...
echo 📍 Backend will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.

python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
