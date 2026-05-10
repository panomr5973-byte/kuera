# Mirofish AI - Quick Start Script for PowerShell

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  🐟 Mirofish AI - Smart Aquaculture System" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$BackendPort = 8000
$FrontendPort = 8501

# Check Python
$PythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $PythonVersion" -ForegroundColor Green

# Setup Backend
$BackendPath = Join-Path $PSScriptRoot "backend"
$VenvPath = Join-Path $BackendPath "venv"

if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $VenvPath
}

# Activate and install dependencies
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
& $ActivateScript

# Check if dependencies installed
$FastapiPath = Join-Path $VenvPath "Lib\site-packages\fastapi"
if (-not (Test-Path $FastapiPath)) {
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    pip install -r (Join-Path $BackendPath "requirements.txt")
}

# Start Backend
Write-Host "🚀 Starting Backend Server on port $BackendPort..." -ForegroundColor Green
$BackendJob = Start-Job -ScriptBlock {
    param($Path, $Activate, $Port)
    & $Activate
    Set-Location $Path
    python main.py
} -ArgumentList $BackendPath, $ActivateScript, $BackendPort

# Wait for backend
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend
$BackendHealth = Invoke-RestMethod -Uri "http://localhost:$BackendPort/health" -ErrorAction SilentlyContinue
if ($BackendHealth) {
    Write-Host "✅ Backend is running!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Backend might not be ready yet" -ForegroundColor Yellow
}

# Start Frontend
$FrontendPath = Join-Path $PSScriptRoot "frontend"
Write-Host "🌐 Starting Frontend Dashboard on port $FrontendPort..." -ForegroundColor Green

$FrontendJob = Start-Job -ScriptBlock {
    param($Path, $Activate)
    & $Activate
    Set-Location $Path
    streamlit run app.py
} -ArgumentList $FrontendPath, $ActivateScript

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ✅ Mirofish AI Started Successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  📊 Backend API:   http://localhost:$BackendPort" -ForegroundColor White
Write-Host "  🖥️  Frontend:      http://localhost:$FrontendPort" -ForegroundColor White
Write-Host "  📚 API Docs:      http://localhost:$BackendPort/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services..." -ForegroundColor Yellow

# Keep script running
while ($true) {
    Start-Sleep -Seconds 1
    
    # Check if jobs are still running
    if ($BackendJob.State -eq "Failed") {
        Write-Host "❌ Backend job failed" -ForegroundColor Red
        Receive-Job $BackendJob
    }
    if ($FrontendJob.State -eq "Failed") {
        Write-Host "❌ Frontend job failed" -ForegroundColor Red
        Receive-Job $FrontendJob
    }
}
