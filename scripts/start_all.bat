@echo off
echo 🚀 Starting K-OSMOS Full Stack Application...
echo.
echo This will start both backend and frontend servers
echo.

REM Start backend in background
echo 1️⃣  Starting Backend (FastAPI)...
start "K-OSMOS Backend" cmd /c "call start_backend.bat"

REM Wait for backend to be ready
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Backend is running
) else (
    echo ⚠️  Backend might not be fully ready yet
)

echo.

REM Start frontend in background
echo 2️⃣  Starting Frontend (Next.js)...
start "K-OSMOS Frontend" cmd /c "call start_frontend.bat"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✨ K-OSMOS is now running!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🌐 Frontend:  http://localhost:3000
echo 🔌 Backend:   http://localhost:8000
echo 📚 API Docs:  http://localhost:8000/docs
echo.
echo Press any key to stop all servers...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pause >nul

REM Kill processes (basic cleanup)
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo Servers stopped.
