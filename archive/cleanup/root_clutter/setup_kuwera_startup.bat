@echo off
chcp 65001 >nul
title KUWERA AI - Setup Auto Startup
color 0A
cls

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║              KUWERA AI - Setup Auto Startup                      ║
echo ║                                                                  ║
echo ║         12 Models ^| Evolution ^| Web Interface                   ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Not running as Administrator
    echo Some features may require admin privileges.
    echo.
    pause
    cls
)

cd /d "%~dp0"

echo [1/5] Checking environment...
echo ----------------------------------------

if not exist "ai_env\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup first.
    pause
    exit /b 1
)

echo [OK] Virtual environment found
echo.

echo [2/5] Checking models...
echo ----------------------------------------

set model_count=0
for %%f in (models\llm\*.gguf) do set /a model_count+=1

echo [OK] Found %model_count% models
echo.

echo [3/5] Creating startup scripts...
echo ----------------------------------------

:: Create startup batch
echo @echo off > "start_kuwera_auto.bat"
echo title KUWERA AI - Auto Start >> "start_kuwera_auto.bat"
echo color 0A >> "start_kuwera_auto.bat"
echo cd /d "C:\AI-Project" >> "start_kuwera_auto.bat"
echo echo. >> "start_kuwera_auto.bat"
echo echo ============================================ >> "start_kuwera_auto.bat"
echo echo    KUWERA AI - Starting Services >> "start_kuwera_auto.bat"
echo echo ============================================ >> "start_kuwera_auto.bat"
echo echo. >> "start_kuwera_auto.bat"
echo "ai_env\Scripts\python.exe" kuwera_autostart.py >> "start_kuwera_auto.bat"
echo echo. >> "start_kuwera_auto.bat"
echo pause >> "start_kuwera_auto.bat"

echo [OK] Created: start_kuwera_auto.bat

:: Create silent startup VBS
echo Set WshShell = CreateObject("WScript.Shell") > "start_kuwera_silent.vbs"
echo WshShell.Run chr(34) ^& "C:\AI-Project\start_kuwera_auto.bat" ^& Chr(34), 0 >> "start_kuwera_silent.vbs"
echo Set WshShell = Nothing >> "start_kuwera_silent.vbs"

echo [OK] Created: start_kuwera_silent.vbs
echo.

echo [4/5] Setup Windows Startup...
echo ----------------------------------------
echo.
echo Pilih metode startup:
echo.
echo [1] Startup Folder (Rekomendasi)
echo     - Jalan otomatis saat user login
echo     - Tampilkan console window
echo.
echo [2] Task Scheduler
echo     - Jalan dengan privilege lebih tinggi
echo     - Bisa diatur delay/jadwal
echo.
echo [3] Keduanya
echo.
echo [4] Skip (manual start saja)
echo.
set /p choice="Pilih (1-4): "

if "%choice%"=="1" goto startup_folder
if "%choice%"=="2" goto task_scheduler
if "%choice%"=="3" goto both_methods
if "%choice%"=="4" goto skip_startup
goto invalid_choice

:startup_folder
echo.
echo Setting up Startup Folder...
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy /Y "start_kuwera_silent.vbs" "%STARTUP_FOLDER%\KUWERA_AI_AutoStart.vbs" >nul
echo [OK] Added to Startup Folder
echo    Location: %STARTUP_FOLDER%\KUWERA_AI_AutoStart.vbs
goto setup_complete

:task_scheduler
echo.
echo Setting up Task Scheduler...
echo [INFO] Creating scheduled task...

schtasks /create /tn "KUWERA_AI_AutoStart" /tr "C:\AI-Project\start_kuwera_silent.vbs" /sc onlogon /rl highest /f >nul 2>&1

if %errorlevel% equ 0 (
    echo [OK] Task created successfully
    echo    Task name: KUWERA_AI_AutoStart
) else (
    echo [WARNING] Failed to create task (may need admin rights)
)
goto setup_complete

:both_methods
echo.
echo Setting up both methods...
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy /Y "start_kuwera_silent.vbs" "%STARTUP_FOLDER%\KUWERA_AI_AutoStart.vbs" >nul
echo [OK] Added to Startup Folder

schtasks /create /tn "KUWERA_AI_AutoStart" /tr "C:\AI-Project\start_kuwera_silent.vbs" /sc onlogon /rl highest /f >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Task Scheduler created
)
goto setup_complete

:skip_startup
echo.
echo [INFO] Skipping Windows startup setup
echo You can start manually with: start_kuwera_auto.bat
goto setup_complete

:invalid_choice
echo.
echo [ERROR] Invalid choice. Skipping startup setup.
goto setup_complete

:setup_complete
echo.
echo [5/5] Finalizing setup...
echo ----------------------------------------

:: Create desktop shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\KUWERA AI.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "C:\AI-Project\start_kuwera_auto.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "C:\AI-Project" >> CreateShortcut.vbs
echo oLink.Description = "KUWERA AI - 12 Model Evolution System" >> CreateShortcut.vbs
echo oLink.IconLocation = "shell32.dll,14" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs >nul
del CreateShortcut.vbs

echo [OK] Desktop shortcut created
echo.

echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                    SETUP COMPLETE!                               ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo INFORMASI:
echo -----------
echo Models:      12 AI Models (29.45 GB)
echo Web UI:      http://localhost:5000
echo Health:      python kuwera_health_check.py
echo.
echo STARTUP OPTIONS:
echo ----------------
echo Manual:      start_kuwera_auto.bat
echo Auto:        Saat login Windows (jika di-setup)
echo.
echo FILES CREATED:
echo ---------------
echo - start_kuwera_auto.bat
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\KUWERA_AI_AutoStart.vbs" (
    echo - Startup Folder shortcut ✓
)
schtasks /query /tn "KUWERA_AI_AutoStart" >nul 2>&1
if %errorlevel% equ 0 (
    echo - Task Scheduler entry ✓
)
echo - Desktop shortcut ✓
echo.

set /p start_now="Jalankan KUWERA sekarang? (y/n): "
if /i "%start_now%"=="y" (
    echo.
    echo Starting KUWERA AI...
    start_kuwera_auto.bat
) else (
    echo.
    echo Setup selesai. Jalankan 'start_kuwera_auto.bat' untuk memulai.
    pause
)
