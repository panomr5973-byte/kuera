@echo off
REM ============================================================
REM Setup Windows Auto-Startup
REM Menambahkan AI App ke Windows Startup
REM ============================================================

echo ========================================
echo Setup Windows Auto-Startup
echo ========================================
echo.

REM Method 1: Startup Folder (User)
echo [1/3] Adding to Startup Folder...
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_NAME=SelfEvolvingAI.lnk

REM Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_DIR%\\%SHORTCUT_NAME%'); $Shortcut.TargetPath = 'C:\\AI-Project\\start_ai_app.bat'; $Shortcut.WorkingDirectory = 'C:\\AI-Project'; $Shortcut.WindowStyle = 7; $Shortcut.IconLocation = '%SystemRoot%\\System32\\SHELL32.dll,14'; $Shortcut.Save()"

if %ERRORLEVEL% EQU 0 (
    echo [OK] Startup shortcut created!
    echo     Location: %STARTUP_DIR%\%SHORTCUT_NAME%
) else (
    echo [WARN] Failed to create shortcut
)

echo.
echo [2/3] Creating Task Scheduler entry...

REM Method 2: Task Scheduler (More reliable)
REM Delete existing task if exists
schtasks /delete /tn "SelfEvolvingAI" /f >NUL 2>&1

REM Create new task - Run at logon, with highest privileges
schtasks /create /tn "SelfEvolvingAI" /tr "C:\AI-Project\start_ai_app.bat" /sc ONLOGON /rl HIGHEST /f

if %ERRORLEVEL% EQU 0 (
    echo [OK] Task Scheduler entry created!
    echo     Name: SelfEvolvingAI
    echo     Trigger: At logon
) else (
    echo [WARN] Failed to create scheduled task (may need admin rights)
)

echo.
echo [3/3] Testing startup file...
if exist "C:\AI-Project\start_ai_app.bat" (
    echo [OK] startup file exists
) else (
    echo [FAIL] start_ai_app.bat not found!
    exit /b 1
)

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Next time you login, AI App will auto-start!
echo.
echo Manual start now?
choice /c YN /m "Run AI App now?"
if %ERRORLEVEL% EQU 1 (
    start "AutoStartup-AI" cmd /c "C:\AI-Project\start_ai_app.bat"
)

echo.
echo To disable auto-start:
echo   - Delete shortcut: %STARTUP_DIR%\%SHORTCUT_NAME%
echo   - Or run: schtasks /delete /tn "SelfEvolvingAI" /f
pause
