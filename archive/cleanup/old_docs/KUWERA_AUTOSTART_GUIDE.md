# KUWERA AI - Auto Startup Guide

Panduan lengkap untuk menjalankan KUWERA AI secara otomatis dengan 12 model dan web interface.

---

## 📋 Ringkasan Sistem

| Komponen | Deskripsi |
|----------|-----------|
| **Models** | 12 AI Models (29.45 GB) |
| **Web Interface** | Flask server di port 5000 |
| **Auto Restart** | Jika crash, otomatis restart |
| **Health Monitor** | Cek status setiap 30 detik |
| **Evolution Tracking** | Pembelajaran dari setiap interaksi |

---

## 🚀 Cara 1: Setup Auto-Startup (Direkomendasikan)

### Langkah 1: Jalankan Setup Script

Buka Command Prompt, lalu jalankan:

```batch
cd C:\AI-Project
setup_kuwera_startup.bat
```

Ikuti instruksi:
1. Pilih metode startup (Startup Folder atau Task Scheduler)
2. Setup akan membuat shortcut di desktop
3. Pilih apakah mau jalankan sekarang

### Langkah 2: Verifikasi

Setelah setup selesai, cek status:

```bash
python kuwera_health_check.py
```

Output yang diharapkan:
```
======================================================================
  KUWERA AI - HEALTH CHECK
======================================================================
  Time: 2026-04-11 20:30:00

  🌐 WEB SERVER
  ------------------------------------------------------------------
  Status:     🟢 RUNNING
  URL:        http://localhost:5000
  Interactions: 0
  Avg Rating:   0.00

  🤖 MODELS
  ------------------------------------------------------------------
  Total Models:   12
  Total Size:     29.45 GB
  Indonesian:     7
  Multilingual:   10
  Coding:         1
  Bartowski:      4

  💾 DATABASES
  ------------------------------------------------------------------
  evolution    🟢 0 interactions
  knowledge    🟢 0 facts, 0 topics

  🚀 AUTOSTART SERVICE
  ------------------------------------------------------------------
  web_server   🟢 running
```

### Langkah 3: Akses Web Interface

Buka browser dan akses:

```
http://localhost:5000
```

Atau dari device lain dalam jaringan yang sama:

```
http://<IP_KOMPUTER>:5000
```

---

## 📋 Cara 2: Manual Start (Alternatif)

Jika tidak ingin auto-start, jalankan manual:

```batch
cd C:\AI-Project

# Cara 1: Jalankan semua service
python kuwera_autostart.py

# Cara 2: Hanya web server
python kuwera_web_server.py
```

---

## 📁 File yang Dibuat

| File | Fungsi |
|------|--------|
| `kuwera_autostart.py` | Launcher utama dengan auto-restart |
| `kuwera_health_check.py` | Cek status sistem |
| `setup_kuwera_startup.bat` | Setup script Windows |
| `start_kuwera_auto.bat` | Batch file untuk start manual |
| `start_kuwera_silent.vbs` | Silent startup (tanpa console) |

---

## 🔄 Daily Workflow

### Pagi: Cek Status

```batch
cd C:\AI-Project
python kuwera_health_check.py
```

### Siang: Gunakan Web Interface

1. Buka `http://localhost:5000`
2. Pilih model dari sidebar kiri
3. Chat dengan AI
4. Lihat evolution real-time di sidebar kanan

### Sore: Cek Pembelajaran

Lihat file:
- `data/knowledge_base.json` - Fakta yang dipelajari
- `logs/kuwera/` - Log harian

---

## 🛠️ Troubleshooting

### Masalah: "Port 5000 sudah digunakan"

**Solusi:**
```batch
# Cek yang pakai port 5000
netstat -ano | findstr :5000

# Kill process (ganti <PID> dengan nomor dari perintah di atas)
taskkill /PID <PID> /F
```

### Masalah: "Web server tidak jalan otomatis"

**Solusi:**
```batch
# Cek Task Scheduler
schtasks /query /tn "KUWERA_AI_AutoStart"

# Cek Startup Folder
dir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

# Jalankan manual untuk lihat error
start_kuwera_auto.bat
```

### Masalah: "Model tidak ditemukan"

**Solusi:**
```batch
# Verifikasi model ada
ls models/llm/*.gguf

# Jika kosong, download models:
hf download bartowski/Qwen2.5-7B-Instruct-GGUF Qwen2.5-7B-Instruct-Q4_K_M.gguf --local-dir models/llm
```

### Masalah: "Database error"

**Solusi:**
```batch
# Database akan dibuat otomatis saat pertama kali
# Jika error, hapus dan buat ulang:
rm data/kuera_evolution.db
rm data/knowledge_base.json

# Restart server
```

---

## 📊 Monitoring

### Health Check

```batch
python kuwera_health_check.py
```

### Status File

```batch
type logs\kuwera\status.json
```

### Log Files

```batch
# Log terbaru
type logs\kuwera\kuwera_20260411.log

# Semua log
dir logs\kuwera\
```

---

## ⚙️ Konfigurasi

### Ganti Port

Edit `kuwera_web_server.py`:
```python
app.run(host="0.0.0.0", port=5001, ...)  # Ganti ke 5001
```

### Disable Auto-Restart

Edit `kuwera_autostart.py`:
```python
max_restarts = 0  # Set ke 0 untuk disable
```

### Tambah Service Baru

Edit `SERVICES` di `kuwera_autostart.py`:
```python
SERVICES = {
    'web_server': {...},
    'my_service': {
        'name': 'My Service',
        'script': 'my_script.py',
        'port': 8080,
        'required': False
    }
}
```

---

## 🔐 Security Notes

1. **Firewall**: Port 5000 terbuka untuk localhost dan network lokal
2. **Access Control**: Web interface tidak memiliki autentikasi (untuk local use)
3. **Data Privacy**: Semua data tersimpan lokal di folder `data/`

---

## 📅 Maintenance

### Setiap Minggu

```batch
# Archive old logs
mkdir logs\archive 2>nul
move logs\kuwera\*.log logs\archive\

# Cek disk space
dir models\llm\
```

### Setiap Bulan

```batch
# Backup databases
copy data\kuera_evolution.db backups\
copy data\knowledge_base.json backups\

# Update dependencies
ai_env\Scripts\pip install --upgrade -r requirements.txt
```

---

## 🎯 Quick Reference

| Perintah | Fungsi |
|----------|--------|
| `python kuwera_autostart.py` | Start semua service |
| `python kuwera_health_check.py` | Cek status |
| `python kuwera_web_server.py` | Start web saja |
| `taskkill /F /IM python.exe` | Stop semua Python |
| `schtasks /run /tn "KUWERA_AI_AutoStart"` | Jalankan scheduled task |

---

## ✅ Checklist Setup

- [ ] Jalankan `setup_kuwera_startup.bat`
- [ ] Verifikasi dengan `python kuwera_health_check.py`
- [ ] Test web interface: `http://localhost:5000`
- [ ] Restart komputer dan cek auto-start
- [ ] Test dari device lain dalam jaringan

---

**Setup selesai! KUWERA AI akan jalan otomatis setiap hari.** 🎉
