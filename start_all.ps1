# K-OSMOS Full Stack Application Starter for Windows PowerShell
Write-Host "🚀 Starting K-OSMOS Full Stack Application..." -ForegroundColor Green
Write-Host ""
Write-Host "This will start both backend and frontend servers" -ForegroundColor Cyan
Write-Host ""

Write-Host "Choose how to start the servers:" -ForegroundColor Yellow
Write-Host "1. Start both in separate terminal windows (Recommended)" -ForegroundColor White
Write-Host "2. Start backend only" -ForegroundColor White
Write-Host "3. Start frontend only" -ForegroundColor White
Write-Host "4. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 Starting both servers in separate windows..." -ForegroundColor Green
        
        # Start backend in new window
        Write-Host "1️⃣  Opening Backend (FastAPI) in new window..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-File", "start_backend.ps1"
        
        Start-Sleep 3
        
        # Start frontend in new window
        Write-Host "2️⃣  Opening Frontend (Next.js) in new window..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-File", "start_frontend.ps1"
        
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host "✨ K-OSMOS servers are starting!" -ForegroundColor Green
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🌐 Frontend:  http://localhost:3000" -ForegroundColor Green
        Write-Host "🔌 Backend:   http://localhost:8000" -ForegroundColor Green
        Write-Host "📚 API Docs:  http://localhost:8000/docs" -ForegroundColor Green
        Write-Host ""
        Write-Host "Each server runs in its own window. Close the windows to stop them." -ForegroundColor Yellow
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        
        # Wait and then open browser
        Write-Host ""
        Write-Host "⏳ Waiting for servers to start..." -ForegroundColor Yellow
        Start-Sleep 10
        
        Write-Host "🌐 Opening frontend in browser..." -ForegroundColor Green
        Start-Process "http://localhost:3000"
    }
    
    "2" {
        Write-Host ""
        Write-Host "🔌 Starting Backend only..." -ForegroundColor Yellow
        & ".\start_backend.ps1"
    }
    
    "3" {
        Write-Host ""
        Write-Host "🌐 Starting Frontend only..." -ForegroundColor Yellow
        & ".\start_frontend.ps1"
    }
    
    "4" {
        Write-Host "👋 Goodbye!" -ForegroundColor Green
        exit 0
    }
    
    default {
        Write-Host "❌ Invalid choice. Exiting..." -ForegroundColor Red
        exit 1
    }
}