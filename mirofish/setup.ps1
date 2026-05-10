# Mirofish AI - Setup Script for PowerShell
# Run this first to setup the environment

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Mirofish AI - Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $PythonVersion = python --version 2>&1
    Write-Host "OK $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR Python not found. Please install Python 3.11+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "Setting up Backend..." -ForegroundColor Yellow
$BackendPath = Join-Path $PSScriptRoot "backend"
$VenvPath = Join-Path $BackendPath "venv"

# Create virtual environment
if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
& $ActivateScript

pip install --upgrade pip
pip install -r (Join-Path $BackendPath "requirements.txt")

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "OK Backend setup complete" -ForegroundColor Green

# Create database directory
$DatabasePath = Join-Path $PSScriptRoot "database"
if (-not (Test-Path $DatabasePath)) {
    New-Item -ItemType Directory -Path $DatabasePath | Out-Null
}

# Copy environment file
$EnvExample = Join-Path $BackendPath ".env.example"
$EnvFile = Join-Path $BackendPath ".env"
if (-not (Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "OK Created .env file (please edit if needed)" -ForegroundColor Green
}

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Setup Complete" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start Mirofish AI, run:" -ForegroundColor Cyan
Write-Host "  .\start-fixed.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or manually:" -ForegroundColor Cyan
Write-Host "  1. Backend: cd backend; .\venv\Scripts\activate; python main.py" -ForegroundColor White
Write-Host "  2. Frontend: cd frontend; streamlit run app.py" -ForegroundColor White
