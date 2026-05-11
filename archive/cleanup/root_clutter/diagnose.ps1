# Diagnose Script - Cari tahu kenapa crash
# Jalankan: .\diagnose.ps1

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AI App - Diagnose & Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Set-Location C:\AI-Project

# 1. Check Python
Write-Host "`n[1/5] Checking Python..." -ForegroundColor Yellow
$python = .\ai_env\Scripts\python.exe --version 2>&1
Write-Host "    $python"

# 2. Check dependencies
Write-Host "`n[2/5] Checking dependencies..." -ForegroundColor Yellow
$deps = @("fastapi", "uvicorn", "pandas", "sklearn", "streamlit", "schedule")
foreach ($dep in $deps) {
    try {
        $null = .\ai_env\Scripts\python.exe -c "import $dep" 2>&1
        Write-Host "    [OK] $dep" -ForegroundColor Green
    } catch {
        Write-Host "    [MISSING] $dep" -ForegroundColor Red
    }
}

# 3. Check files
Write-Host "`n[3/5] Checking files..." -ForegroundColor Yellow
$files = @(
    "run_self_evolving.py",
    "start_scheduler.py",
    "self_evolving\app.py",
    "logs\feedback\self_improve.db"
)
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "    [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "    [MISSING] $file" -ForegroundColor Red
    }
}

# 4. Check port 8000
Write-Host "`n[4/5] Checking port 8000..." -ForegroundColor Yellow
$portCheck = netstat -ano | findstr :8000
if ($portCheck) {
    Write-Host "    [WARN] Port 8000 sudah digunakan!" -ForegroundColor Yellow
    Write-Host "    $portCheck" -ForegroundColor Gray
    Write-Host "`n    Untuk kill process, jalankan sebagai Admin:" -ForegroundColor Cyan
    Write-Host "    taskkill /F /IM python.exe" -ForegroundColor White
} else {
    Write-Host "    [OK] Port 8000 available" -ForegroundColor Green
}

# 5. Test API startup (5 seconds only)
Write-Host "`n[5/5] Testing API startup..." -ForegroundColor Yellow
Write-Host "    Menjalankan 5 detik test..." -ForegroundColor Gray

$testJob = Start-Job -ScriptBlock {
    Set-Location C:\AI-Project
    .\ai_env\Scripts\python.exe run_self_evolving.py 2>&1
} -Name "Test-API"

Start-Sleep -Seconds 5

$jobOutput = Receive-Job $testJob
Stop-Job $testJob -ErrorAction SilentlyContinue
Remove-Job $testJob -ErrorAction SilentlyContinue

if ($jobOutput -match "Error" -or $jobOutput -match "Traceback") {
    Write-Host "    [FAIL] API ada error saat startup:" -ForegroundColor Red
    $jobOutput | Select-Object -Last 20 | ForEach-Object { Write-Host "      $_" -ForegroundColor Red }
} else {
    Write-Host "    [OK] API startup test passed" -ForegroundColor Green
}

# Summary & Fix
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Summary & Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nSolusi cepat:" -ForegroundColor White
Write-Host "  1. Kill semua Python:     taskkill /F /IM python.exe" -ForegroundColor Yellow
Write-Host "  2. Start dengan simple:   .\start_simple.ps1" -ForegroundColor Green
Write-Host "  3. Atau start manual:     .\ai_env\Scripts\python.exe run_self_evolving.py" -ForegroundColor Green

Write-Host "`nJika masih crash, cek log:" -ForegroundColor White
Write-Host "  type logs\startup\*.log" -ForegroundColor Gray

Write-Host ""
