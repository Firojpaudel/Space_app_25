@echo off
echo 🔧 Setting up K-OSMOS Development Environment...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ and try again.
    pause
    exit /b 1
)

echo ✅ Python and Node.js found
echo.

REM Setup backend
echo 🐍 Setting up Backend...
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Setup environment file
if not exist ".env" (
    echo 📋 Creating .env from .env.example...
    copy .env.example .env
    echo ⚠️  Please edit .env file and add your API keys
)

echo.

REM Setup frontend
echo 🎨 Setting up Frontend...
cd frontend

echo 📥 Installing Node.js dependencies...
npm install

if not exist ".env.local" (
    echo 📋 Creating .env.local from .env.example...
    copy .env.example .env.local
)

cd ..

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys (Gemini, Pinecone)
echo 2. Run: scripts\start_all.bat
echo.
pause
