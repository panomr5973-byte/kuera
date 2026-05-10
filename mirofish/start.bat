@echo off
REM Mirofish AI - Quick Start Script for Windows

echo ==========================================
echo  🐟 Mirofish AI - Smart Aquaculture System
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "backend\venv\Scripts\activate" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

REM Activate virtual environment
echo Activating virtual environment...
call backend\venv\Scripts\activate

REM Install dependencies if needed
if not exist "backend\venv\Lib\site-packages\fastapi" (
    echo Installing backend dependencies...
    pip install -r backend\requirements.txt
)

REM Start Backend in new window
echo Starting Backend Server...
start "Mirofish Backend" cmd /k "cd backend && call venv\Scripts\activate && python main.py"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Start Frontend in new window
echo Starting Frontend Dashboard...
start "Mirofish Frontend" cmd /k "cd frontend && call ..\backend\venv\Scripts\activate && streamlit run app.py"

echo.
echo ==========================================
echo  ✅ Mirofish AI Started!
echo ==========================================
echo.
echo  Backend API:   http://localhost:8000
echo  Frontend:      http://localhost:8501
echo  API Docs:      http://localhost:8000/docs
echo.
echo  Press any key to exit this window...
pause > nul
