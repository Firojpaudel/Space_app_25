#!/bin/bash

echo "🚀 Starting K-OSMOS Backend API..."
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python not found. Please install Python 3.9+"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
if [ ! -f "venv/installed" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    pip install fastapi uvicorn
    touch venv/installed
    echo ""
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Please create .env file with required API keys"
    echo "See .env.example for reference"
    echo ""
fi

echo "🌐 Starting FastAPI server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend && python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
