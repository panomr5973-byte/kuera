#!/usr/bin/env pwsh
# KUERA AI — Push to GitHub Helper
# Usage: .\push_to_github.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   KUERA AI — Push to GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Git tidak ditemukan. Install dulu: https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

# 2. Check repo
if (-not (Test-Path .git)) {
    Write-Host "[ERROR] Ini bukan git repository. Jalankan dari root project." -ForegroundColor Red
    exit 1
}

# 3. Show current status
Write-Host "[INFO] Git config saat ini:" -ForegroundColor Yellow
Write-Host "  Email: $(git config user.email)"
Write-Host "  Name:  $(git config user.name)"
Write-Host ""

# 4. Check if remote exists
$remotes = git remote -v 2>$null
if ($remotes) {
    Write-Host "[INFO] Remote yang sudah terdaftar:" -ForegroundColor Yellow
    Write-Host $remotes
    Write-Host ""
    $useExisting = Read-Host "Gunakan remote yang sudah ada? (y/n)"
    if ($useExisting -eq "y") {
        Write-Host "[OK] Push ke remote existing..." -ForegroundColor Green
        git push -u origin master
        Write-Host "[DONE] Push selesai!" -ForegroundColor Green
        exit 0
    }
}

# 5. Guide user to create repo
Write-Host "[STEP 1] Buat repository baru di GitHub:" -ForegroundColor Magenta
Write-Host "  1. Buka browser: https://github.com/new" -ForegroundColor White
Write-Host "  2. Isi Repository name: AI-Project (atau nama lain)" -ForegroundColor White
Write-Host "  3. Jangan centang 'Add a README' (sudah ada)" -ForegroundColor White
Write-Host "  4. Klik 'Create repository'" -ForegroundColor White
Write-Host ""

# 6. Ask for repo URL
$repoUrl = Read-Host "[STEP 2] Paste repository URL (https atau ssh)"

if (-not $repoUrl) {
    Write-Host "[ERROR] URL tidak boleh kosong." -ForegroundColor Red
    exit 1
}

# 7. Add remote and push
Write-Host ""
Write-Host "[STEP 3] Menambahkan remote dan push..." -ForegroundColor Green

try {
    git remote add origin $repoUrl
    Write-Host "[OK] Remote 'origin' ditambahkan." -ForegroundColor Green
} catch {
    Write-Host "[WARN] Remote mungkin sudah ada, coba update..." -ForegroundColor Yellow
    git remote set-url origin $repoUrl
}

# Verify
$verify = git remote -v
Write-Host "[INFO] Remote sekarang:"
Write-Host $verify
Write-Host ""

# Push
Write-Host "[STEP 4] Push ke GitHub..." -ForegroundColor Green
Write-Host "  (Ini mungkin meminta username dan password/token GitHub)" -ForegroundColor Gray
try {
    git push -u origin master
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   SUCCESS! Backup ke GitHub selesai." -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "[ERROR] Push gagal. Kemungkinan penyebab:" -ForegroundColor Red
    Write-Host "  1. Belum login GitHub di git" -ForegroundColor Yellow
    Write-Host "  2. URL repo salah" -ForegroundColor Yellow
    Write-Host "  3. Repo sudah punya commit (README auto-generated)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Solusi untuk kasus 3:" -ForegroundColor Cyan
    Write-Host "  git pull origin master --rebase" -ForegroundColor White
    Write-Host "  git push -u origin master" -ForegroundColor White
    Write-Host ""
    Write-Host "Solusi untuk login:" -ForegroundColor Cyan
    Write-Host "  Gunakan Personal Access Token sebagai password:" -ForegroundColor White
    Write-Host "  https://github.com/settings/tokens" -ForegroundColor White
}
