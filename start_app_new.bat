@echo off
echo Starting K-OSMOS with Fresh Environment...

REM Kill any existing processes
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 >nul

REM Activate the fresh environment
call conda activate space_bio

REM Start the app
echo.
echo ✅ Environment: space_bio
echo ✅ Port: 8505
echo ✅ URL: http://localhost:8505
echo.
echo Opening browser...
start "" http://localhost:8505

echo Running K-OSMOS...
streamlit run kosmos_app.py --server.port 8505