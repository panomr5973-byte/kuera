@echo off
echo ==========================================
echo   Mirofish AI - Fix Dependencies
echo ==========================================
echo.

cd /d D:\workspace\AI-Project\mirofish\backend

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing compatible packages for Python 3.14...
pip install fastapi uvicorn python-multipart sqlalchemy aiosqlite paho-mqtt numpy pandas scikit-learn python-dotenv pydantic pydantic-settings httpx python-jose passlib python-dateutil pytest pytest-asyncio

echo.
echo ==========================================
echo   Dependencies Updated
echo ==========================================
pause
