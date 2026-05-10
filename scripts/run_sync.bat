@echo off
REM Auto-Sync Script Runner
REM Jalankan ini untuk sync manual, atau setup scheduled task dengan admin rights

echo ===========================================
echo AI Model Sync - Manual Run
echo ===========================================
echo.

cd /d C:\AI-Project
python scripts\sync_models.py

echo.
echo ===========================================
echo Sync completed!
echo ===========================================
pause
