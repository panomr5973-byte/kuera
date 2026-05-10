# KUERA Quick Upload to Terabox
# Usage: .\quick_upload.ps1 -Type models
#        .\quick_upload.ps1 -Type database
#        .\quick_upload.ps1 -Type all

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("models", "database", "logs", "all", "test")]
    [string]$Type,

    [string]$CookiesFile = "cookies.json"
)

$ErrorActionPreference = "Stop"

function Test-Cookies {
    if (-not (Test-Path $CookiesFile)) {
        Write-Host "[ERROR] $CookiesFile not found!" -ForegroundColor Red
        Write-Host "[INFO] Please login to https://www.terabox.com and copy your 'ndus' cookie." -ForegroundColor Yellow
        Write-Host "[INFO] Then create $CookiesFile from cookies.json.template" -ForegroundColor Yellow
        exit 1
    }
}

function Test-Python {
    try {
        $py = python --version 2>&1
        Write-Host "[OK] $py" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Python not found in PATH" -ForegroundColor Red
        exit 1
    }
}

function Install-Deps {
    Write-Host "[INFO] Checking dependencies..." -ForegroundColor Cyan
    pip install -q -r requirements.txt
}

function Test-Login {
    Write-Host "[INFO] Testing Terabox login..." -ForegroundColor Cyan
    $output = python upload.py --file "../../data/kuera_database.db" --remote "/KUERA_Backup/test" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Login failed! Check your cookies." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Login successful!" -ForegroundColor Green
}

# Main
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  KUERA Quick Upload to Terabox" -ForegroundColor Cyan
Write-Host "  Account: panomr5973@gmail.com" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Test-Cookies
Test-Python
Install-Deps

switch ($Type) {
    "test" {
        Test-Login
    }
    "models" {
        Write-Host "[UPLOAD] All LLM models..." -ForegroundColor Green
        python upload.py --folder "../../models/llm" --remote "/KUERA_Backup/models/llm" --pattern "*.gguf"
    }
    "database" {
        Write-Host "[UPLOAD] Main database..." -ForegroundColor Green
        python upload.py --file "../../data/kuera_database.db" --remote "/KUERA_Backup/data"
    }
    "logs" {
        Write-Host "[UPLOAD] Application logs..." -ForegroundColor Green
        python upload.py --folder "../../logs" --remote "/KUERA_Backup/logs" --pattern "*.log"
    }
    "all" {
        Write-Host "[UPLOAD] Full backup (everything)..." -ForegroundColor Green
        python upload.py --batch batch_list.json
    }
}

Write-Host ""
Write-Host "[DONE] Upload process completed." -ForegroundColor Green
