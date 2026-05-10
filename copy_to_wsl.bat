@echo off
chcp 65001 >nul
echo ==========================================
echo  COPY AI AUDIT TOOLKIT KE WSL
echo ==========================================
echo.

REM Buat folder di WSL
echo 📁 Membuat folder di WSL...
wsl mkdir -p ~/ai-audit/templates

REM Copy file-file utama
echo 📄 Copy file Python...

wsl cp /mnt/c/AI-Project/audit_toolkit_complete.py ~/ai-audit/
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Gagal copy audit_toolkit_complete.py, mencoba cara lain...
    copy /Y "C:\AI-Project\audit_toolkit_complete.py" "%TEMP%\audit_toolkit_complete.py"
    wsl cp /mnt/c/temp/audit_toolkit_complete.py ~/ai-audit/ 2>nul
)

wsl cp /mnt/c/AI-Project/template_audit_spi.py ~/ai-audit/ 2>nul
wsl cp /mnt/c/AI-Project/template_audit_kinerja.py ~/ai-audit/ 2>nul
wsl cp /mnt/c/AI-Project/template_master.py ~/ai-audit/ 2>nul
wsl cp /mnt/c/AI-Project/README_AUDIT_AI.md ~/ai-audit/ 2>nul

echo.
echo ✅ Copy selesai!
echo.
echo 📂 File tersedia di WSL: ~/ai-audit/
echo.
echo Untuk menjalankan:
echo   1. Buka WSL: wsl
echo   2. cd ~/ai-audit
echo   3. source venv/bin/activate
echo   4. python template_master.py
echo.
pause
