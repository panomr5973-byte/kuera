# 🚀 Auto-Startup Guide - Self-Evolving AI App

Panduan lengkap untuk menjalankan aplikasi AI secara otomatis setiap kali komputer dinyalakan.

---

## 📋 CARA 1: Setup Auto-Startup (Direkomendasikan)

### Langkah 1: Jalankan Setup Script

Buka **Command Prompt sebagai Admin**, lalu jalankan:

```batch
cd C:\AI-Project
setup_windows_startup.bat
```

Ini akan:
- ✅ Membuat shortcut di Startup Folder
- ✅ Membuat Task Scheduler entry
- ✅ Menanyakan apakah mau jalankan sekarang

### Langkah 2: Verifikasi Setup

Restart komputer atau logout-login, lalu cek:

```powershell
# Cek apakah aplikasi berjalan
python check_health.py
```

Output yang diharapkan:
```
============================================================
HEALTH CHECK - Self-Evolving AI
============================================================
📡 API Server:
  [OK] Running
       Interactions: 5
       Model: model_20260402_100050
       Satisfaction: 100.0%

⏰ Scheduler:
  [RUNNING] Started: 2026-04-02T10:00:00

💾 Database:
  [OK] Total: 5 interactions
       With feedback: 2
       Today: 3
```

---

## 📋 CARA 2: Manual Startup (Alternatif)

Jika setup otomatis gagal, jalankan manual:

### Opsi A: Startup Folder

1. Tekan `Win + R`, ketik: `shell:startup`
2. Copy file `start_ai_app.bat` ke folder tersebut
3. Selesai! Aplikasi akan jalan otomatis saat login

### Opsi B: Task Scheduler

1. Buka Task Scheduler (cari di Start Menu)
2. Create Basic Task:
   - **Name**: SelfEvolvingAI
   - **Trigger**: When I log on
   - **Action**: Start a program
   - **Program**: `C:\AI-Project\start_ai_app.bat`
3. Centang "Run with highest privileges"
4. Save

---

## 📋 CARA 3: One-Time Launch (Tanpa Auto-Start)

Jika tidak mau auto-start, jalankan manual setiap kali:

```powershell
cd C:\AI-Project

# Terminal 1: Jalankan API + Scheduler sekaligus
python auto_startup.py

# Atau pisah (untuk debugging):
# Terminal 1: python run_self_evolving.py
# Terminal 2: python start_scheduler.py
```

---

## 🔧 File yang Dibuat

| File | Fungsi |
|------|--------|
| `auto_startup.py` | Launcher utama dengan auto-restart |
| `start_ai_app.bat` | Batch file untuk Windows |
| `setup_windows_startup.bat` | Setup script otomatis |
| `verify_and_start.py` | Verifikasi & start interaktif |
| `check_health.py` | Cek status aplikasi |

---

## 📊 Daily Workflow (Setelah Auto-Start Aktif)

### Pagi: Cek Status

```powershell
cd C:\AI-Project
python check_health.py
```

### Siang: Interact & Feedback

Gunakan browser atau curl:

```bash
# Chat dengan AI
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d "{\"query\":\"Halo\",\"session_id\":\"user1\"}"

# Beri feedback
curl -X POST "http://localhost:8000/feedback" -H "Content-Type: application/json" -d "{\"interaction_id\":1,\"feedback\":1}"
```

Atau buka Dashboard:

```powershell
streamlit run app/dashboard.py
# Buka http://localhost:8501 → tab "Feedback & Improvement"
```

### Sore: Cek Evolusi

```powershell
# Lihat model baru
ls models/*.pkl

# Cek registry
type models\model_registry.json

# Lihat log retraining
type logs\feedback\scheduler.log
```

---

## 🛠️ Troubleshooting

### Masalah: "App tidak jalan otomatis"

**Solusi:**
1. Cek Task Scheduler:
   ```powershell
   schtasks /query /tn "SelfEvolvingAI"
   ```

2. Cek Startup Folder:
   ```powershell
   ls "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
   ```

3. Jalankan manual untuk lihat error:
   ```powershell
   C:\AI-Project\start_ai_app.bat
   ```

### Masalah: "Port 8000 sudah digunakan"

**Solusi:**
```powershell
# Cek yang pakai port 8000
netstat -ano | findstr :8000

# Kill process (ganti <PID> dengan nomor dari perintah di atas)
taskkill /PID <PID> /F
```

### Masalah: "Virtual environment tidak ditemukan"

**Solusi:**
```powershell
cd C:\AI-Project
python -m venv ai_env
ai_env\Scripts\pip install -r requirements.txt
```

### Masalah: "Model tidak berkembang"

**Cek:**
```powershell
# 1. Cukup data?
sqlite3 logs\feedback\self_improve.db "SELECT COUNT(*) FROM interactions WHERE user_feedback IS NOT NULL;"

# Butuh minimal 50 feedback untuk trigger retrain

# 2. Scheduler berjalan?
tasklist | findstr python

# 3. Cek log
type logs\startup\startup_20260402.log
```

---

## 📅 Weekly Maintenance

### Setiap Senin:
```powershell
# Archive old logs
mkdir logs\archive
move logs\startup\*.log logs\archive\

# Clean old models (keep last 5)
# Manual: Hapus model lama di folder models/
```

### Setiap Bulan:
```powershell
# Backup database
copy logs\feedback\self_improve.db backups\self_improve_backup_%date%.db

# Update dependencies
ai_env\Scripts\pip install --upgrade -r requirements.txt
```

---

## 🎯 Quick Reference

| Perintah | Fungsi |
|----------|--------|
| `python check_health.py` | Cek status aplikasi |
| `python verify_and_start.py` | Verifikasi & start manual |
| `python auto_startup.py` | Start semua service |
| `taskkill /F /IM python.exe` | Stop semua Python |
| `schtasks /run /tn "SelfEvolvingAI"` | Jalankan scheduled task |

---

## 🔐 Security Notes

1. **Jangan jalankan sebagai Admin** kecuali diperlukan
2. **Firewall**: Port 8000 (API) dan 8501 (Dashboard) terbuka untuk localhost
3. **Backup**: Database SQLite di `logs/feedback/` - backup secara berkala

---

## ✅ Checklist Setup

- [ ] Jalankan `setup_windows_startup.bat`
- [ ] Restart komputer
- [ ] Verifikasi dengan `python check_health.py`
- [ ] Test chat: `curl http://localhost:8000/chat`
- [ ] Test dashboard: `streamlit run app/dashboard.py`
- [ ] Buat 50+ interactions untuk trigger retrain

**Setup selesai! Aplikasi akan jalan otomatis setiap hari.** 🎉
