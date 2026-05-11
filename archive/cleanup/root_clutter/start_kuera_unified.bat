@echo off
chcp 65001 >nul
title KUERA AI v3.1
cls

cd /d "%~dp0"

echo =========================================
echo   KUERA AI v3.1 — Unified Desktop
echo =========================================
echo.
echo [INFO] Buka browser ke: http://localhost:7777
echo [INFO] Tekan Ctrl+C untuk berhenti
echo.

python main.py
