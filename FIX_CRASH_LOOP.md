# FIX: Crash Loop Issue

## Masalah
Auto-start script menunjukkan "crash and restart in 5 seconds" terus-menerus.

## Penyebab
1. **Port 8000 sudah digunakan** oleh proses Python lain
2. Auto-restart script (`auto_startup.py`) mencoba restart terus-menerus

## Solusi Cepat

### Step 1: Kill Semua Python Process

Buka **Command Prompt sebagai Administrator**:

```cmd
taskkill /F /IM python.exe
taskkill /F /IM pythonw.exe
```

Atau di PowerShell:
```powershell
Get-Process python* | Stop-Process -Force
```

### Step 2: Verifikasi Port Bebas

```cmd
netstat -ano | findstr :8000
```

Jika tidak ada output, port sudah bebas.

### Step 3: Jalankan dengan Script Simple

```powershell
cd C:\AI-Project
.\start_simple.ps1
```

Pilih:
- **1** = API Server saja
- **2** = Scheduler saja  
- **3** = Keduanya (API di background, Scheduler di foreground)

---

## Alternative: Jalankan Manual (Terminal Terpisah)

**Terminal 1:**
```powershell
cd C:\AI-Project
.\ai_env\Scripts\python.exe run_self_evolving.py
```

**Terminal 2:**
```powershell
cd C:\AI-Project
.\ai_env\Scripts\python.exe start_scheduler.py
```

**Terminal 3:**
```powershell
cd C:\AI-Project
.\ai_env\Scripts\streamlit.exe run app\dashboard.py
```

---

## Cek Status

```powershell
python check_health.py
```

---

## Hindari Crash Loop di Masa Depan

1. **Jangan gunakan `auto_startup.py`** jika tidak perlu auto-restart
2. Gunakan `start_simple.ps1` untuk kontrol manual
3. Selalu kill process lama sebelum start baru

---

## File yang Direkomendasikan

| File | Gunakan | Hindari |
|------|---------|---------|
| `start_simple.ps1` | ✅ | - |
| `run_self_evolving.py` | ✅ | - |
| `start_scheduler.py` | ✅ | - |
| `auto_startup.py` | - | ✅ (jika ada crash loop) |
