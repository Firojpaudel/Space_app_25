# K-OSMOS Frontend Starter for Windows PowerShell
Write-Host "🚀 Starting K-OSMOS Frontend..." -ForegroundColor Green
Write-Host ""

# Check if frontend directory exists
if (!(Test-Path "frontend")) {
    Write-Host "❌ Error: frontend directory not found" -ForegroundColor Red
    exit 1
}

Set-Location frontend

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>$null
    $npmVersion = npm --version 2>$null
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
    Write-Host "✅ npm found: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Node.js/npm not found. Please install Node.js" -ForegroundColor Red
    exit 1
}

# Check if node_modules exists
if (!(Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    Write-Host ""
}

# Check if .env.local exists
if (!(Test-Path ".env.local")) {
    if (Test-Path ".env.example") {
        Write-Host "⚙️  Creating .env.local from example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env.local"
        Write-Host ""
    }
}

Write-Host "🌐 Starting Next.js development server..." -ForegroundColor Green
Write-Host "📍 Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

npm run dev