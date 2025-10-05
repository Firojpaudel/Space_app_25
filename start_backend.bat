@echo off
echo 🚀 Starting K-OSMOS Backend API...
echo.

REM Check if conda environment is active
if not "%CONDA_DEFAULT_ENV%"=="" (
    echo ✅ Conda environment active: %CONDA_DEFAULT_ENV%
) else (
    echo ⚠️  Activating conda environment spacey...
    call conda activate spacey
)

REM Install requirements
if exist requirements.txt (
    echo 📦 Installing Python dependencies...
    pip install -r requirements.txt
    pip install fastapi uvicorn
    echo.
)

REM Check if .env exists
if not exist .env (
    echo ⚠️  Warning: .env file not found
    echo Please create .env file with required API keys
    echo See .env.example for reference
    echo.
)

echo 🌐 Starting FastAPI server...
echo 📍 API will be available at: http://localhost:8000
echo 📚 API docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python api_server.py