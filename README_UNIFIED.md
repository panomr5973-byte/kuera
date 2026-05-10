# KUERA UNIFIED DESKTOP v3.0

## Integrasi: KueraClaw | Kuera-AI Evolusi | Kuera API | Admin Panel

---

## 🎯 Apa Ini?

**KUERA UNIFIED DESKTOP** adalah single-process orchestrator yang menyatukan seluruh ekosistem KUERA AI dalam satu Control Panel terpusat.

Sebelumnya, Anda menjalankan banyak file `.bat` secara bersamaan yang menyebabkan:
- Konflik port (5000, 8000, 8501, dll)
- Duplikasi proses Python
- Crash loop dan resource leak
- Sulit monitoring

**Unified Desktop** memperbaiki semua itu.

---

## 🚀 Cara Menjalankan

```bash
# Cara 1: Double-click
start_kuera_unified.bat

# Cara 2: Command line
cd D:\workspace\ai_core\AI-Project
python kuera_unified_desktop.py
```

Control Panel akan terbuka otomatis di browser: **http://localhost:7777**

---

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────────┐
│              KUERA UNIFIED DESKTOP v3.0                 │
│                   (Port 7777)                           │
│                      │                                  │
│         ┌────────────┼────────────┐                     │
│         ▼            ▼            ▼                     │
│    ┌────────┐   ┌────────┐   ┌────────┐                │
│    │Process │   │  Web   │   │ Health │                │
│    │Manager │   │Control │   │ Monitor│                │
│    └────┬───┘   │ Panel  │   └────────┘                │
│         │       └────────┘                             │
│    ┌────┴────────────────────────────────────┐         │
│    │                                         │         │
│    ▼         ▼         ▼         ▼           ▼         │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐    ┌──────┐      │
│ │ API  │ │ Web  │ │Stream│ │Admin │    │Evolu-│      │
│ │ 8000 │ │ 5000 │ │ 8501 │ │Panel │    │ tion │      │
│ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘    └──┬───┘      │
│    │        │        │        │            │           │
│    ▼        ▼        ▼        ▼            ▼           │
│ ┌────────────────────────────────────────────────┐     │
│ │           12 AI Models (29.45 GB)              │     │
│ │   Qwen, Llama, SeaLLM, Merak, Gemma, etc.      │     │
│ └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Services yang Dikelola

| Service | Port | Deskripsi | Auto-Start |
|---------|------|-----------|------------|
| **Kuera Production API** | 8000 | FastAPI dengan auth & rate limiting | ❌ |
| **Kuera Real API** | 8001 | Real API server (uvicorn) | ❌ |
| **Kuera Web Server v2** | 5000 | Flask web dengan persona chat | ❌ |
| **Kuera Streamlit Dashboard** | 8501 | Analytics dashboard | ❌ |
| **Kuera Admin Panel** | 5000 | Admin control center | ❌ |
| **Kuera Evolution Engine** | - | Self-evolution tracking | ❌ |
| **KueraClaw Multi-Model CLI** | - | Interactive CLI | ❌ |

> Semua service dimatikan secara default untuk menghindari konflik. Anda aktifkan satu per satu dari Control Panel.

---

## 🎮 Control Panel Features

### 1. Service Manager
- Start / Stop / Restart setiap service
- Auto-restart jika crash (max 5x)
- Health check via port probing
- Uptime tracking

### 2. Unified Logs
- Real-time log aggregation dari semua service
- Color-coded (error = merah, warning = kuning)
- Filter per service

### 3. Model Registry
- Menampilkan 12 model yang tersedia
- Total size: 29.45 GB
- Kategorisasi: Indonesian, Multilingual, Coding, dll.

### 4. Quick Access Links
- Langsung buka Web Interface, API Docs, Dashboard

---

## ⚠️ Troubleshooting

### Port Conflict
Jika ada pesan "Address already in use":
```powershell
# Cek port
Get-NetTCPConnection -LocalPort 5000,7777,8000,8001,8501

# Kill semua proses AI-Project
Get-Process python | Where-Object { $_.Path -like "*AI-Project*" } | Stop-Process -Force
```

### Service Crash Loop
Unified Desktop akan auto-restart service yang crash (maksimal 5 kali). Jika terus crash:
1. Cek log di Control Panel
2. Pastikan dependency terinstall
3. Jalankan script secara manual untuk debug

### Model Not Found
Pastikan folder `models/llm/` berisi file `.gguf`. Registry otomatis terbaca dari `models/llm/model_registry_active.json`.

---

## 🗂️ File Baru

| File | Fungsi |
|------|--------|
| `kuera_unified_desktop.py` | Main orchestrator & Control Panel server |
| `start_kuera_unified.bat` | Launcher one-click |
| `README_UNIFIED.md` | Dokumentasi ini |

---

## 🧹 File Bat Lama (Redundant)

File `.bat` lama yang **sebaiknya tidak dijalankan langsung** lagi:
- `START_KUWERA.bat`
- `start_ai_app.bat`
- `start_kuwera_auto.bat`
- `start_admin_panel.bat`
- `start_kuera_web.bat`
- `start_kuwera_web.bat`
- `start_kuwera_v2.bat`
- `start_production.bat`

Gunakan **Unified Desktop** untuk mengelola semuanya.

---

## 🔧 Environment

- **Python**: 3.10+ (terdeteksi otomatis)
- **Virtual Env**: `ai_env` (jika ada, digunakan otomatis)
- **OS**: Windows 10/11
- **Working Dir**: `D:\workspace\ai_core\AI-Project`

---

**KUERA UNIFIED DESKTOP v3.0**  
*Dibuat: 2026-05-05*  
*Lokasi: `D:\workspace\ai_core\AI-Project`*
