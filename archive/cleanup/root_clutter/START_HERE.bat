@echo off
chcp 65001 >nul
REM ============================================================
REM START HERE - Self-Evolving AI App Launcher
REM ============================================================
:menu
echo.
echo ========================================
echo   Self-Evolving AI - Quick Start
echo ========================================
echo.
echo [1] Setup Auto-Startup (Jalan otomatis setiap hari)
echo [2] Verifikasi dan Start Manual
echo [3] Cek Status (Health Check)
echo [4] Buka Dashboard
echo [5] Stop Semua Service
echo [6] Lihat Log
echo [0] Keluar
echo.
set /p choice=Pilih (0-6): 

cd /d "C:\AI-Project"

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto verify
if "%choice%"=="3" goto health
if "%choice%"=="4" goto dashboard
if "%choice%"=="5" goto stop
if "%choice%"=="6" goto logs
if "%choice%"=="0" goto exit

echo Pilihan tidak valid!
pause
goto menu

:setup
echo.
echo [Setup Auto-Startup]...
call setup_windows_startup.bat
pause
goto menu

:verify
echo.
echo [Verifikasi dan Start]...
call ai_env\Scripts\activate.bat
python verify_and_start.py
pause
goto menu

:health
echo.
echo [Health Check]...
call ai_env\Scripts\activate.bat
python check_health.py
pause
goto menu

:dashboard
echo.
echo [Buka Dashboard]...
start http://localhost:8501
call ai_env\Scripts\activate.bat
streamlit run app/dashboard.py
pause
goto menu

:stop
echo.
echo [Stop Services]...
taskkill /F /IM python.exe 2>nul
echo [OK] Semua service dihentikan
pause
goto menu

:logs
echo.
echo [Lihat Log]...
if exist logs\startup\*.log (
    type logs\startup\*.log 2>nul | more
) else (
    echo Log belum ada. Jalankan service dulu.
)
pause
goto menu

:exit
echo.
echo Terima kasih!
timeout /t 2 >nul
exit /b 0
