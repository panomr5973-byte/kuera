@echo off
chcp 65001 >nul
title KUERA UNIFIED DESKTOP v3.0 - Integrated Control Panel
cls

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                                                                      ║
echo ║           KUERA UNIFIED DESKTOP v3.0                                 ║
echo ║                                                                      ║
echo ║   Integrasi: KueraClaw ^| Kuera-AI Evolusi ^| Kuera API             ║
echo ║                                                                      ║
echo ║   Control Panel : http://localhost:7777                              ║
echo ║   Web Interface : http://localhost:5000                              ║
echo ║   API Docs      : http://localhost:8000/docs                         ║
echo ║   Dashboard     : http://localhost:8501                              ║
echo ║                                                                      ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    pause
    exit /b 1
)

echo [OK] Python ditemukan
echo [START] Memulai Unified Control Panel...
echo.
echo Tunggu sebentar, browser akan terbuka otomatis.
echo.

REM Install dependencies if needed
python -c "import flask, flask_cors" 2>nul
if errorlevel 1 (
    echo [INFO] Installing Flask dependencies...
    pip install flask flask-cors -q
)

REM Start unified desktop
python kuera_unified_desktop.py

echo.
echo [EXIT] Unified Desktop telah berhenti.
pause
