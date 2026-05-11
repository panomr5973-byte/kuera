# QuickStart.ps1 - Self-Evolving AI Launcher
# Jalankan: .\QuickStart.ps1

param(
    [Parameter()]
    [ValidateSet("api", "scheduler", "dashboard", "health", "setup", "stop")]
    [string]$Action = "menu"
)

$ErrorActionPreference = "Stop"

function Show-Menu {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "   Self-Evolving AI - Quick Start" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[1] Start API Server"
    Write-Host "[2] Start Scheduler"
    Write-Host "[3] Start Dashboard"
    Write-Host "[4] Health Check"
    Write-Host "[5] Setup Auto-Startup"
    Write-Host "[6] Stop All Services"
    Write-Host "[0] Exit"
    Write-Host ""
    
    $choice = Read-Host "Pilih (0-6)"
    
    switch ($choice) {
        "1" { Start-Api }
        "2" { Start-Scheduler }
        "3" { Start-Dashboard }
        "4" { Test-Health }
        "5" { Setup-AutoStart }
        "6" { Stop-Services }
        "0" { exit }
        default { 
            Write-Host "Pilihan tidak valid!" -ForegroundColor Red
            Start-Sleep -Seconds 1
            Show-Menu
        }
    }
}

function Start-Api {
    Write-Host "`n[START] API Server..." -ForegroundColor Green
    Set-Location C:\AI-Project
    & .\ai_env\Scripts\python.exe run_self_evolving.py
}

function Start-Scheduler {
    Write-Host "`n[START] Scheduler..." -ForegroundColor Green
    Set-Location C:\AI-Project
    & .\ai_env\Scripts\python.exe start_scheduler.py
}

function Start-Dashboard {
    Write-Host "`n[START] Dashboard..." -ForegroundColor Green
    Set-Location C:\AI-Project
    Start-Process "http://localhost:8501"
    & .\ai_env\Scripts\streamlit.exe run app\dashboard.py
}

function Test-Health {
    Write-Host "`n[CHECK] Health Check..." -ForegroundColor Yellow
    Set-Location C:\AI-Project
    & .\ai_env\Scripts\python.exe check_health.py
    Write-Host "`nTekan Enter untuk kembali..."
    Read-Host
    Show-Menu
}

function Setup-AutoStart {
    Write-Host "`n[SETUP] Auto-Startup..." -ForegroundColor Green
    Set-Location C:\AI-Project
    & .\setup_windows_startup.bat
    Write-Host "`nTekan Enter untuk kembali..."
    Read-Host
    Show-Menu
}

function Stop-Services {
    Write-Host "`n[STOP] Menghentikan services..." -ForegroundColor Red
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "[OK] Services dihentikan" -ForegroundColor Green
    Start-Sleep -Seconds 2
    Show-Menu
}

# Main
Set-Location C:\AI-Project

Show-Menu
