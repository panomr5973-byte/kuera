@echo off
REM Mirofish AI - Simple Setup Script

echo ==========================================
echo   Mirofish AI - Setup
echo ==========================================
echo.

cd /d D:\workspace\AI-Project\mirofish

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

echo.
echo Setting up Backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Creating database directory...
if not exist ..\database mkdir ..\database

echo Creating .env file...
if not exist .env copy .env.example .env

echo.
echo ==========================================
echo   Setup Complete
echo ==========================================
echo.
echo To start Mirofish AI:
echo   1. Open TWO terminal windows
echo   2. Terminal 1: cd backend ^&^& call venv\Scripts\activate.bat ^&^& python main.py
echo   3. Terminal 2: cd frontend ^&^& call ..\backend\venv\Scripts\activate.bat ^&^& streamlit run app.py
echo.
pause
