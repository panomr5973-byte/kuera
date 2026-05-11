# Simple Starter - Tanpa auto-restart loop
# Jalankan ini di PowerShell: .\start_simple.ps1

param(
    [switch]$Api,
    [switch]$Scheduler,
    [switch]$Both
)

$ErrorActionPreference = "Stop"

function Test-ApiHealth {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 3 -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Start-ApiService {
    Write-Host "`n[START] Memulai API Server..." -ForegroundColor Green
    Write-Host "URL: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "Tekan Ctrl+C untuk berhenti`n" -ForegroundColor Yellow
    
    Set-Location C:\AI-Project
    
    # Cek apakah sudah berjalan
    if (Test-ApiHealth) {
        Write-Host "[INFO] API sudah berjalan!" -ForegroundColor Yellow
        return
    }
    
    try {
        & .\ai_env\Scripts\python.exe run_self_evolving.py
    } catch {
        Write-Host "[ERROR] API Server error: $_" -ForegroundColor Red
        Write-Host "`nCoba jalankan manual untuk lihat detail error:" -ForegroundColor Yellow
        Write-Host "  .\ai_env\Scripts\python.exe run_self_evolving.py" -ForegroundColor Cyan
    }
}

function Start-SchedulerService {
    Write-Host "`n[START] Memulai Scheduler..." -ForegroundColor Green
    Write-Host "Log: logs\feedback\scheduler.log" -ForegroundColor Cyan
    Write-Host "Tekan Ctrl+C untuk berhenti`n" -ForegroundColor Yellow
    
    Set-Location C:\AI-Project
    
    try {
        & .\ai_env\Scripts\python.exe start_scheduler.py
    } catch {
        Write-Host "[ERROR] Scheduler error: $_" -ForegroundColor Red
    }
}

# Main
Set-Location C:\AI-Project

Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Self-Evolving AI - Simple Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($Api) {
    Start-ApiService
}
elseif ($Scheduler) {
    Start-SchedulerService
}
elseif ($Both) {
    Write-Host "`n[MODE] Start Both (API + Scheduler)" -ForegroundColor Magenta
    
    # Start API in background job
    $apiJob = Start-Job -ScriptBlock {
        Set-Location C:\AI-Project
        & .\ai_env\Scripts\python.exe run_self_evolving.py 2>&1
    } -Name "API-Server"
    
    Write-Host "[OK] API Server started in background (Job)" -ForegroundColor Green
    
    # Wait a bit for API to start
    Start-Sleep -Seconds 3
    
    # Start Scheduler in foreground
    Write-Host "[OK] Starting Scheduler...`n" -ForegroundColor Green
    & .\ai_env\Scripts\python.exe start_scheduler.py
    
    # Cleanup
    Stop-Job $apiJob -ErrorAction SilentlyContinue
    Remove-Job $apiJob -ErrorAction SilentlyContinue
}
else {
    # Interactive menu
    Write-Host "`nPilih mode:" -ForegroundColor White
    Write-Host "  [1] API Server saja" -ForegroundColor Green
    Write-Host "  [2] Scheduler saja" -ForegroundColor Blue
    Write-Host "  [3] Keduanya (API + Scheduler)" -ForegroundColor Magenta
    Write-Host "  [4] Test Health" -ForegroundColor Yellow
    Write-Host "  [0] Exit" -ForegroundColor Gray
    Write-Host ""
    
    $choice = Read-Host "Pilih (0-4)"
    
    switch ($choice) {
        "1" { Start-ApiService }
        "2" { Start-SchedulerService }
        "3" { 
            Write-Host "`n[INFO] Mode: API di background, Scheduler di foreground" -ForegroundColor Cyan
            $apiJob = Start-Job -ScriptBlock {
                Set-Location C:\AI-Project
                & .\ai_env\Scripts\python.exe run_self_evolving.py 2>&1 | Out-File logs\api_output.log -Append
            } -Name "API-Server"
            
            Start-Sleep -Seconds 3
            
            if (Test-ApiHealth) {
                Write-Host "[OK] API berjalan!`n" -ForegroundColor Green
            } else {
                Write-Host "[WARN] API mungkin butuh waktu lebih lama...`n" -ForegroundColor Yellow
            }
            
            Start-SchedulerService
            
            Stop-Job $apiJob -ErrorAction SilentlyContinue
            Remove-Job $apiJob -ErrorAction SilentlyContinue
        }
        "4" { 
            & .\ai_env\Scripts\python.exe check_health.py
            Write-Host "`nTekan Enter untuk kembali..."
            Read-Host
            & $PSCommandPath
        }
        "0" { exit }
        default { 
            Write-Host "Pilihan tidak valid!" -ForegroundColor Red
            Start-Sleep -Seconds 2
            & $PSCommandPath
        }
    }
}
