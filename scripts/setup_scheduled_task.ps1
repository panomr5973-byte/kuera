# Setup Scheduled Task untuk Auto-Sync Model
# Jalankan sebagai Administrator

$taskName = "AI-Model-Sync"
$taskDescription = "Auto-sync AI models dari C: ke D: setiap hari"

# Path ke Python dan script
$pythonPath = "C:\Python314\python.exe"
$scriptPath = "C:\AI-Project\scripts\sync_models.py"

# Buat action
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath

# Buat trigger (setiap hari jam 2 pagi)
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00"

# Buat settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register task
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description $taskDescription -RunLevel Highest
    Write-Host "[OK] Scheduled task '$taskName' berhasil dibuat!" -ForegroundColor Green
    Write-Host "[INFO] Task akan berjalan setiap hari jam 02:00" -ForegroundColor Cyan
} catch {
    Write-Host "[ERROR] Gagal membuat scheduled task: $_" -ForegroundColor Red
}

# Verifikasi
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName, State, LastRunTime, NextRunTime | Format-Table
