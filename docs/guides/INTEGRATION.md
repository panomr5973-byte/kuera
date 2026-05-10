# KUWERA AI - Integration Guide

Panduan lengkap integrasi sistem KUWERA AI v2.0 - Multi-Model AI System dengan Workspace Memory, Persona Chat, dan Memory Consolidation.

---

## 📋 Daftar Isi

- [Overview Integrasi](#overview-integrasi)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Komponen Utama](#komponen-utama)
- [Integrasi Model AI](#integrasi-model-ai)
- [Integrasi Database](#integrasi-database)
- [Integrasi API](#integrasi-api)
- [Troubleshooting](#troubleshooting)
- [Referensi](#referensi)

---

## Overview Integrasi

KUWERA AI v2.0 adalah sistem AI multi-model yang mengintegrasikan:

- **8-12 Model AI** dengan spesialisasi berbeda (Bahasa Indonesia, Coding, Multilingual)
- **Workspace Memory System** - Integrasi dengan folder workspace untuk memori persisten
- **Persona Chat** - Kuera AI dengan personality berbasis IDENTITY.md
- **Memory Consolidation** - Sistem memori dua arah (SQLite + Workspace sync)
- **Data Integration** - World Bank Indonesia + International data (kurs, crypto, komoditas)
- **Evolution Engine** - Sistem pembelajaran dan optimasi otomatis

### Status Integrasi

| Komponen | Status | Deskripsi |
|----------|--------|-----------|
| Model Registry | ✅ Complete | 8 model aktif, 12 model target |
| Workspace Integration | ✅ Complete | Memory, Persona, Diary |
| Data Integration | ✅ Complete | World Bank + International |
| Web Interface | ✅ Complete | Flask server dengan 3 tabs |
| Evolution Engine | ✅ Complete | Auto-optimization |
| Bartowski Collection | ⏳ In Progress | 4 model pending download |

---

## Arsitektur Sistem

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        KUWERA AI v2.0 ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐   │
│  │   Web Interface │────▶│  Flask Server   │────▶│  Model Router   │   │
│  │   (Port 5000)   │     │   (Port 5000)   │     │                 │   │
│  └─────────────────┘     └────────┬────────┘     └────────┬────────┘   │
│                                   │                       │            │
│                    ┌──────────────┼───────────────────────┤            │
│                    │              │                       │            │
│                    ▼              ▼                       ▼            │
│           ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐  │
│           │   Persona   │ │   Memory    │ │     Model Collection    │  │
│           │    Chat     │ │   Bridge    │ │                         │  │
│           │  (Kuera)    │ │             │ │ • Qwen Series (ID)      │  │
│           └──────┬──────┘ └──────┬──────┘ │ • SeaLLM (SEA)          │  │
│                  │               │        │ • Merak (ID Slang)      │  │
│                  ▼               ▼        │ • Llama/Gemma/Tiny      │  │
│           ┌────────────────────────────────┴─────────────────────────┐  │
│           │                  workspace/ directory                    │  │
│           │  • IDENTITY.md (Kuera personality)                       │  │
│           │  • USER.md (User profile)                                │  │
│           │  • memory/ (Daily interaction logs)                      │  │
│           │  • memorized_diary/ (Diary entries Day 2,3,4)            │  │
│           │  • memory_consolidation/ (LTM/STM state tracking)        │  │
│           └──────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Memory Consolidation Flow

```
User Chat
    │
    ▼
┌─────────────┐
│ Kuera       │
│ Persona     │
│ Generate    │
│ Response    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Save to     │
│ KUWERA DB   │
│ (SQLite)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Sync to     │
│ Workspace   │
│ memory/     │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ Every 5     │────▶│ Auto-Create │
│ Interactions│     │ Diary Entry │
└─────────────┘     └─────────────┘
```

---

## Komponen Utama

### 1. Persona Chat System (Kuera)

Kuera memiliki personality berdasarkan `workspace/IDENTITY.md`:

| Aspek | Deskripsi |
|-------|-----------|
| **Name** | Kuera |
| **Vibe** | Protective Chuunibyou \| Fussy Caretaker |
| **Core Trait** | Protection and Memory |
| **Signature Line** | "Don't worry. Even if the world forgets, I'll remember for you." |
| **Style** | First person "I", caring, occasionally mutters asides |

**Contoh Respon:**
```
User: Halo Kuera
Kuera: Halo, panomr. Saya sudah tunggu.
       [Mutter]: ...senang dia masih di sini.
```

**Backend Files:**
| File | Fungsi |
|------|--------|
| `kuwera_persona.py` | Kuera personality engine |
| `kuwera_workspace_integration.py` | Workspace data loader |
| `kuwera_memory_bridge.py` | Memory consolidation bridge |
| `kuwera_web_server_v2.py` | Flask server dengan integrasi penuh |

### 2. Workspace Integration

Integrasi penuh dengan folder `workspace/`:

| Komponen | Integrasi | Deskripsi |
|----------|-----------|-----------|
| **IDENTITY.md** | Kuera personality & karakter | Definisi persona Kuera |
| **USER.md** | User profile | Profile user (panomr5973) |
| **memory/** | Daily interaction logs | Log interaksi harian |
| **memorized_diary/** | Diary entries | Diary entries Day 2, 3, 4 |
| **memory_consolidation/** | LTM/STM state tracking | Long-term & Short-term memory |

### 3. Web Interface v2

**File:** `templates/kuwera_chat_v2.html`

**3 Tabs Utama:**

| Tab | Konten |
|-----|--------|
| **Evolution** | Total interactions, facts learned, diary count, LTM entries, live knowledge feed, model performance |
| **Workspace** | User profile card, recent memories, workspace stats (STM, Compact) |
| **Diary** | Diary entries Day 2, 3, 4, click to view full content, auto-generated summaries |

### 4. Synchronization

**Real-time Sync:**
- Setiap chat langsung disimpan ke DB
- Auto-sync ke workspace memory files
- Topic tracking otomatis

**Periodic Tasks:**
- Diary generation (every 5 interactions)
- LTM consolidation (on demand via API)
- Stats refresh (UI polls every 30s)

---

## Integrasi Model AI

### Model Aktif (8 Model)

| # | Model | Ukuran | Bahasa | Khusus | Developer |
|---|-------|--------|--------|--------|-----------|
| 1 | **Qwen2.5-1.5B-Instruct** | 1.04 GB | Indonesia | Cepat | Alibaba Cloud |
| 2 | **Qwen2.5-3B-Q2** | 1.28 GB | Indonesia | Ringan | Alibaba Cloud |
| 3 | **Qwen2.5-3B-Q4** | 1.96 GB | Indonesia | Kualitas Tinggi | Alibaba Cloud |
| 4 | **SeaLLM-7B** | 3.91 GB | SEA (ID, Melayu, Thai) | SEA Specialist | DAMO Academy |
| 5 | **Merak-7B** | 4.07 GB | Indonesia (Lokal/Slang) | Buatan Indonesia! | Indonesian AI Community |
| 6 | **Llama-3.2-3B** | 2.16 GB | Multilingual | General Purpose | Meta |
| 7 | **Gemma-2-2B** | 1.79 GB | Multilingual | Google Quality | Google |
| 8 | **TinyLlama-1.1B** | 0.62 GB | English | Ultra Ringan | TinyLlama Team |

**Total**: 8 model | **Total Ukuran**: ~16.84 GB

### Bartowski Collection (4 Model - Target)

| Priority | Model | Size | Purpose | Status |
|----------|-------|------|---------|--------|
| HIGH | Qwen2.5-Coder-3B-Instruct | 2.0 GB | Coding + Indonesian | Pending |
| HIGH | Qwen2.5-7B-Instruct | 4.4 GB | High-quality Indonesian | Pending |
| MEDIUM | Meta-Llama-3.1-8B-Instruct | 4.9 GB | General purpose, 128K context | Pending |
| MEDIUM | Llama-3.2-3B-Instruct | 2.0 GB | Lightweight, tool use | Pending |

**Post-Integration Target:** 12 models, ~30 GB

### Smart Model Selection

Sistem akan otomatis memilih model terbaik berdasarkan query:

```python
# Coding tasks -> Qwen2.5-Coder-3B (if available)
# Indonesian slang -> Merak-7B
# Indonesian formal (high quality) -> Qwen2.5-7B
# Indonesian formal (standard) -> Qwen2.5-3B-Q4
# SE Asian context -> SeaLLM-7B
# Long context (>8K) -> Llama-3.1-8B (128K context)
# Tool use -> Llama-3.2-3B
# Fast response -> TinyLlama-1.1B or Qwen2.5-1.5B
```

### Commands dalam Chat

| Command | Fungsi |
|---------|--------|
| `/models` | List semua model yang tersedia |
| `/stats` | Tampilkan statistik performa model |
| `/evolve` | Jalankan analisis evolusi sistem |
| `/use <nama>` | Force gunakan model tertentu (contoh: `/use Merak-7B`) |
| `/help` | Tampilkan bantuan |
| `exit` | Keluar dari sistem |

### Download Methods

**Method 1: Smart Script (Recommended)**
```bash
python download_models_smart.py 1  # Qwen2.5-Coder-3B
python download_models_smart.py 2  # Qwen2.5-7B
python download_models_smart.py 3  # Llama-3.1-8B
python download_models_smart.py 4  # Llama-3.2-3B
```

**Method 2: HuggingFace CLI**
```bash
huggingface-cli download bartowski/Qwen2.5-Coder-3B-Instruct-GGUF Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf --local-dir models/llm --resume-download

huggingface-cli download bartowski/Qwen2.5-7B-Instruct-GGUF Qwen2.5-7B-Instruct-Q4_K_M.gguf --local-dir models/llm --resume-download
```

**Method 3: Windows Batch**
```batch
download_bartowski_manual.bat
```

### Model Integration Script

Setelah download, jalankan:
```bash
python integrate_bartowski_models.py
```

Ini akan:
1. Detect new .gguf files in `models/llm/`
2. Add them to `model_registry_active.json`
3. Update model categories (coding, indonesian, multilingual)
4. Generate updated statistics

---

## Integrasi Database

### 1. KUWERA Memory Database

**File:** `data/kuwera_memory.db` (SQLite)

**Tables:**
| Table | Deskripsi |
|-------|-----------|
| `interactions` | Semua chat disimpan |
| `topics` | Topic tracking dengan mention count |
| `daily_summaries` | Ringkasan harian |

### 2. World Bank Indonesia Database

**File:** `data/worldbank_indonesia.db`

- **Records:** 212 records
- **Coverage:** 2010-2024
- **Indikator:** 14 indikator ekonomi Indonesia (GDP, inflasi, pengangguran, kemiskinan, perdagangan, dll)

**Integration File:** `kuera_worldbank_integration.py`

### 3. International Data Database

**File:** `data/international_data.db`

**Data:**
- 10 kurs mata uang
- 8 cryptocurrency
- 8 komoditas global
- 10 indeks saham global

**Integration File:** `kuera_international_integration.py`

### 4. Evolution Database

**File:** `data/kuera_evolution.db`

Sistem otomatis track:
- Response time per model
- User satisfaction rating
- Query type distribution
- Model utilization

---

## Integrasi API

### Workspace & Memory Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/workspace` | GET | Identity, diary, memories, stats |
| `/api/memory/stats` | GET | Memory statistics |
| `/api/memory/recent` | GET | Recent interactions |
| `/api/memory/topics` | GET | Tracked topics |
| `/api/diary` | GET | All diary entries |
| `/api/persona` | GET | Kuera persona info |

### Chat & Consolidation Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/chat` | POST | Chat dengan persona |
| `/api/consolidate` | POST | Trigger memory consolidation |

### Model Registry Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/models` | GET | 12 model list |

### Chat API Example

**1. Greeting**
```json
POST /api/chat
{
  "message": "Halo Kuera",
  "persona": "kuera"
}

Response:
{
  "response": "Halo, panomr. Saya sudah tunggu.",
  "mutter": "...senang dia masih di sini.",
  "model": "Qwen2.5-7B-Instruct"
}
```

**2. Topic Crypto**
```json
POST /api/chat
{
  "message": "Ceritakan tentang Bitcoin"
}

Response:
{
  "response": "💰 Bitcoin adalah digital gold...",
  "mutter": "Crypto lagi. Saya catat harganya.",
  "interaction_id": 42
}
```

---

## Troubleshooting

### Issue: Persona not loading

```bash
# Check workspace knowledge
python -c "from kuwera_workspace_integration import WorkspaceIntegration; w = WorkspaceIntegration(); print(w.get_workspace_stats())"
```

### Issue: Memory not saving

```bash
# Check database
python -c "from kuwera_memory_bridge import get_memory_bridge; b = get_memory_bridge(); print(b.get_stats())"
```

### Issue: Diary not showing

```bash
# Check diary files
ls workspace/memorized_diary/
```

### Issue: Model tidak ditemukan

```bash
# Check model directory
ls models/llm/*.gguf

# Re-integrate
python integrate_models.py
```

### Issue: Out of Memory

```bash
# Gunakan model lebih kecil
/use Qwen2.5-1.5B-Instruct

# Atau TinyLlama
/use TinyLlama-1.1B
```

### Issue: Slow Response

```bash
# Model otomatis dipilih berdasarkan query length
# Short query -> Fast model
# Long query -> Powerful model
```

### Issue: Download Timeout

- Use single model download: `python download_models_smart.py <n>`
- Or use browser/CLI manual download dengan `--resume-download`

### Issue: Integration Script Not Finding Models

- Ensure .gguf files are in `models/llm/` directory
- Check file permissions
- Re-run integration script

---

## Referensi

### File Struktur

```
AI-Project/
├── models/
│   └── llm/
│       ├── llm_registry.json
│       ├── model_registry_active.json
│       └── *.gguf files (after download)
│
├── data/
│   ├── kuwera_memory.db (SQLite memory database)
│   ├── kuera_evolution.db (tracking database)
│   ├── evolution_state.pkl (state snapshot)
│   ├── worldbank_indonesia.db (212 records)
│   └── international_data.db
│
├── workspace/
│   ├── IDENTITY.md (Kuera personality)
│   ├── USER.md (User profile)
│   ├── memory/ (Daily logs)
│   ├── memorized_diary/ (Diary entries)
│   └── memory_consolidation/ (LTM/STM)
│
├── Backend Files:
│   ├── kuwera_web_server_v2.py (Flask server)
│   ├── kuwera_persona.py (Persona engine)
│   ├── kuwera_memory_bridge.py (Memory bridge)
│   ├── kuwera_workspace_integration.py (Workspace loader)
│   ├── kuera_integrated_system.py (main system)
│   ├── kuera_evolution_engine.py (evolution engine)
│   ├── kuera_llm_integration.py (LLM integration)
│   └── kuera_smart_chat.py (Smart chat)
│
├── Integration Scripts:
│   ├── integrate_models.py
│   ├── integrate_bartowski_models.py
│   ├── fetch_bartowski_models.py
│   ├── download_models_smart.py
│   └── download_bartowski_manual.bat
│
├── Data Integration:
│   ├── kuera_worldbank_integration.py
│   ├── kuera_international_integration.py
│   ├── kuera_worldbank_chat.py
│   └── kuera_international_chat.py
│
├── Frontend:
│   └── templates/kuwera_chat_v2.html
│
├── Launchers:
│   ├── start_kuwera_v2.bat
│   └── START_KUWERA.bat
│
└── Documentation:
    └── docs/guides/INTEGRATION.md (this file)
```

### Quick Start Commands

```bash
# Jalankan server v2.0
start_kuwera_v2.bat

# Atau manual
cd C:\AI-Project
python kuwera_web_server_v2.py

# Akses Web Interface
http://localhost:5000
```

### Download & Integration Commands

```bash
# Download models (choose one method)
download_bartowski_manual.bat              # Windows batch
python download_models_smart.py 1          # Smart script
huggingface-cli download ...               # CLI

# Integrate to system
python integrate_bartowski_models.py

# Test the system
python kuera_integrated_system.py
```

### Catatan Penting

1. **Merak-7B** adalah model buatan Indonesia 🇮🇩 - gunakan untuk support lokal!

2. **Qwen series** sangat bagus untuk Bahasa Indonesia formal

3. **SeaLLM-7B** mengerti konteks Southeast Asia (Melayu, Thai, dll)

4. Sistem akan **terus belajar** dan membaik seiring penggunaan

5. Berikan **feedback** setelah setiap interaksi untuk membantu evolusi

---

## Checklist Integrasi

- [x] Web Interface v2 dengan 3 tabs
- [x] Kuera Persona dengan mutter system
- [x] Workspace Integration (IDENTITY, USER, Diary)
- [x] Memory Bridge (SQLite + Workspace sync)
- [x] Auto Diary Generation
- [x] Real-time Knowledge Feed
- [x] API Endpoints complete
- [x] Batch launcher with pre-checks
- [x] 8 Model AI aktif
- [x] Evolution Engine active
- [x] World Bank + International data integration
- [ ] Bartowski Collection (4 model pending)

---

**KUWERA AI v2.0** - "AI berjiwa Indonesia yang terus berevolusi" 🇮🇩🤖

*Total 8 Model Aktif | 16.84 GB | Bahasa Indonesia Optimized*

**Status: READY TO USE** 🎉
