#!/bin/bash

echo "🔧 Setting up K-OSMOS Development Environment..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

echo "✅ Python and Node.js found"
echo ""

# Setup backend
echo "🐍 Setting up Backend..."
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys"
fi

echo ""

# Setup frontend
echo "🎨 Setting up Frontend..."
cd frontend

echo "📥 Installing Node.js dependencies..."
npm install

if [ ! -f ".env.local" ]; then
    echo "📋 Creating .env.local from .env.example..."
    cp .env.example .env.local
fi

cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys (Gemini, Pinecone)"
echo "2. Run: ./scripts/start_all.sh (Linux/Mac) or scripts\\start_all.bat (Windows)"
echo ""
