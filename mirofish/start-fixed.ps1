# Mirofish AI - Fixed Start Script

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Mirofish AI - Starting" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$BackendPath = Join-Path $PSScriptRoot "backend"
$FrontendPath = Join-Path $PSScriptRoot "frontend"
$VenvPath = Join-Path $BackendPath "venv"

# Check if venv exists
if (-not (Test-Path $VenvPath)) {
    Write-Host "ERROR Virtual environment not found. Please run setup.ps1 first" -ForegroundColor Red
    Write-Host "   Command: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

# Start Backend
Write-Host "Starting Backend Server..." -ForegroundColor Green
$BackendProc = Start-Process -FilePath "powershell" -ArgumentList @(
    "-Command",
    "& '$ActivateScript'; Set-Location '$BackendPath'; python main.py"
) -PassThru -WindowStyle Normal

Write-Host "   Backend PID: $($BackendProc.Id)" -ForegroundColor Gray

# Wait for backend to start
Write-Host "Waiting for backend to initialize (5 seconds)" -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend
try {
    $BackendHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "OK Backend is running" -ForegroundColor Green
} catch {
    Write-Host "WARNING Backend might still be starting" -ForegroundColor Yellow
}

# Start Frontend
Write-Host "Starting Frontend Dashboard" -ForegroundColor Green
$FrontendProc = Start-Process -FilePath "powershell" -ArgumentList @(
    "-Command",
    "& '$ActivateScript'; Set-Location '$FrontendPath'; streamlit run app.py"
) -PassThru -WindowStyle Normal

Write-Host "   Frontend PID: $($FrontendProc.Id)" -ForegroundColor Gray

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Mirofish AI Started" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend API:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:      http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Dashboard:     http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "To stop: Close the backend and frontend windows" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to close this window (services will keep running)" -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
