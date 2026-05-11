@echo off
chcp 65001 >nul
title KUERA AI v3.1
cls

echo =========================================
echo   KUERA AI v3.1 — Unified Desktop
echo =========================================
echo.

cd /d "%~dp0"

echo [CHECK] Working directory: %CD%
echo [CHECK] Python path:
where python 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan di PATH.
    echo [ERROR] Install Python 3.10+ atau aktifkan virtual environment.
    pause
    exit /b 1
)

echo [CHECK] Python version:
python --version

echo.
echo [START] Menjalankan KUERA Unified Desktop...
echo [INFO] Buka browser ke: http://localhost:7777
echo [INFO] Tekan Ctrl+C untuk berhenti
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server berhenti dengan error code %errorlevel%
    pause
) else (
    echo.
    echo [INFO] Server dimatikan.
)
