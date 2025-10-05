@echo off
echo 🚀 Starting K-OSMOS Frontend...
echo.

REM Check if frontend directory exists
if not exist frontend (
    echo ❌ Error: frontend directory not found
    pause
    exit /b 1
)

cd frontend

REM Check if node_modules exists
if not exist node_modules (
    echo 📦 Installing dependencies...
    npm install
    echo.
)

REM Check if .env.local exists
if not exist .env.local (
    if exist .env.example (
        echo ⚙️  Creating .env.local from example...
        copy .env.example .env.local
        echo.
    )
)

echo 🌐 Starting Next.js development server...
echo 📍 Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev