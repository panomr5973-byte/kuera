@echo off
chcp 65001 >nul
title KUERA Tailscale Manager
echo ==========================================
echo   KUERA Tailscale Network Manager
echo ==========================================
echo.

if "%~1"=="" goto menu
set ACTION=%~1
goto run

:menu
echo   1. status      - Check tailnet connectivity
echo   2. test-proxy  - Test VPS reverse proxy
echo   3. test-ollama - Test Ollama on VPS
echo   4. ssh         - SSH to VPS via Tailscale
echo   5. machines    - List all tailnet machines
echo   6. test-all    - Full health check
echo.
set /p ACTION="Enter choice (1-6 or name): "

:run
if "%ACTION%"=="1" set ACTION=status
if "%ACTION%"=="2" set ACTION=test-proxy
if "%ACTION%"=="3" set ACTION=test-ollama
if "%ACTION%"=="4" set ACTION=ssh
if "%ACTION%"=="5" set ACTION=machines
if "%ACTION%"=="6" set ACTION=test-all

powershell -ExecutionPolicy Bypass -File "%~dp0kuera_tailscale.ps1" -Action %ACTION%

if errorlevel 1 (
    echo.
    echo [ERROR] Command failed.
)

pause
