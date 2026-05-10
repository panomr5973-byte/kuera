@echo off
chcp 65001 >nul
title KUERA Terabox Backup
echo ==========================================
echo   KUERA Backup to Terabox
echo   Account: panomr5973@gmail.com
echo ==========================================
echo.

:: Check if cookies.json exists
if not exist "cookies.json" (
    echo [ERROR] cookies.json not found!
    echo.
    echo [INFO] Please:
    echo   1. Login to https://www.terabox.com in your browser
    echo   2. Copy your 'ndus' cookie value
    echo   3. Create cookies.json from cookies.json.template
    echo.
    pause
    exit /b 1
)

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    pause
    exit /b 1
)

:: Install dependencies
echo [INFO] Checking dependencies...
pip install -q -r requirements.txt

:: Check login first
echo.
echo [INFO] Checking Terabox login...
python upload.py --file "../../data/kuera_database.db" --remote "/KUERA_Backup/test"
if errorlevel 1 (
    echo.
    echo [ERROR] Login failed! Please update your cookies.json
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   What do you want to backup?
echo ==========================================
echo   1. All models (LLM .gguf files, ~25 GB)
echo   2. Main database (kuera_database.db, ~2.3 GB)
echo   3. All databases
echo   4. Everything (models + databases + logs)
echo   5. Custom batch upload
echo   6. Exit
echo.
set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto models
if "%choice%"=="2" goto maindb
if "%choice%"=="3" goto alldb
if "%choice%"=="4" goto everything
if "%choice%"=="5" goto batch
if "%choice%"=="6" goto end

goto end

:models
echo.
echo [INFO] Uploading all LLM models...
python upload.py --folder "../../models/llm" --remote "/KUERA_Backup/models/llm" --pattern "*.gguf"
goto end

:maindb
echo.
echo [INFO] Uploading main database...
python upload.py --file "../../data/kuera_database.db" --remote "/KUERA_Backup/data"
goto end

:alldb
echo.
echo [INFO] Uploading all databases...
python upload.py --file "../../data/kuera_database.db" --remote "/KUERA_Backup/data"
python upload.py --file "../../data/international_data.db" --remote "/KUERA_Backup/data"
python upload.py --file "../../data/worldbank_indonesia.db" --remote "/KUERA_Backup/data"
python upload.py --file "../../data/kuera_evolution.db" --remote "/KUERA_Backup/data"
goto end

:everything
echo.
echo [INFO] Starting full backup (this will take a while)...
python upload.py --batch batch_list.json
goto end

:batch
echo.
echo [INFO] Running batch upload from batch_list.json...
python upload.py --batch batch_list.json
goto end

:end
echo.
echo [INFO] Backup process completed.
pause
