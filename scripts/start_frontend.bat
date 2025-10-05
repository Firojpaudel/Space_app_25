@echo off
echo 🎨 Starting K-OSMOS Frontend Server...

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
)

REM Check if .env.local exists
if not exist ".env.local" (
    echo 📋 Creating .env.local from .env.example...
    copy .env.example .env.local
)

echo 🚀 Starting Next.js development server...
echo 🌐 Frontend will be available at: http://localhost:3000
echo.

npm run dev
