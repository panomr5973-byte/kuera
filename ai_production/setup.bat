@echo off
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create venv
    pause
    exit /b 1
)
echo Activating venv and installing requirements...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Install failed
    pause
    exit /b 1
)
echo.
echo === SETUP COMPLETE ===
echo To activate: cd c:/AI-Project/ai_production && call venv\Scripts\activate.bat
echo Then: uvicorn app.production_api:app --host 0.0.0.0 --port 8000 --reload
echo or python scripts/watch_evolution.py
pause
