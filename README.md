# KUERA AI — Unified Desktop v3.1

> Local-first AI workstation for government audit workflows (Government Audit Agency Indonesia)

KUERA is a self-contained AI system that runs entirely on your local machine. It integrates local LLMs, audit automation tools, economic data analysis, and a unified control panel into a single workspace.

---

## 🚀 Quick Start

```bash
# Activate environment
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # WSL/Linux

# Start the control panel
python main.py
```

Open `http://localhost:7777` in your browser.

---

## ✨ What You Get

| Feature | Description | Status |
|---------|-------------|--------|
| **Control Panel** | Dark-themed Flask dashboard with real-time service management | ✅ Active |
| **Audit Workflow** | Upload Excel → Run Audit (Keuangan/SPI/Kinerja) → View Charts → Export | ✅ Active |
| **Anomaly Detection** | IQR + Z-Score + Benford's Law fraud detection | ✅ Active |
| **Real-time Charts** | Chart.js visualizations: radar, doughnut, bar, gauge | ✅ Active |
| **World Bank Data** | Indonesia economic indicators with historical trends | ✅ Active |
| **Local LLMs** | Qwen2.5 series (CPU inference via ctransformers) | ✅ Active |
| **Process Manager** | Auto-start, health probes, log aggregation for all services | ✅ Active |
| **Database Maintenance** | Auto-vacuum, indexing, archive old records | ✅ Active |

---

## 📁 Directory Structure

```
AI-Project/
├── main.py                      # ⭐ Entry point — start here
├── config/
│   ├── settings.yaml            # Ports, paths, defaults
│   └── services.yaml            # Service definitions (7 services)
├── src/                         # Active codebase
│   ├── core/                    # Process manager, service registry, logger
│   ├── web/                     # Flask dashboard + REST API
│   ├── data/                    # Audit workflow, WorldBank connector, pipelines
│   ├── models/                  # Model registry
│   └── utils/                   # Config loader, unified logger
├── audit_toolkit.py             # Core: Excel processor + anomaly detection
├── template_audit_spi.py        # SPI audit (COSO framework)
├── template_audit_kinerja.py    # Kinerja audit (scoring A/B/C/D/E)
├── tests/                       # pytest suite (23 tests)
├── scripts/
│   ├── db_maintenance.py        # SQLite optimization
│   ├── terabox/                 # Cloud backup
│   └── tailscale/               # Network tunnels
├── data/                        # Databases & uploads
├── models/llm/                  # GGUF model files (~29 GB)
├── memory/                      # Daily operation logs (.md)
├── docs/                        # Documentation
└── archive/                     # Archived redundant scripts
```

---

## 🔌 Active Ports

| Port | Service | Auto-Start |
|------|---------|------------|
| **7777** | Control Panel (Flask) | ✅ Yes |
| 18789 | WebSocket Gateway | ✅ Yes |
| 8000 | Production API | ❌ No |
| 8001 | Real API v2 | ❌ No |
| 5000 | Web Server v2 | ❌ No |
| 5001 | Admin Panel | ❌ No |
| 8501 | Streamlit Dashboard | ❌ No |

---

## 📊 Audit Workflow

### Via Web UI (Recommended)
1. Open `http://localhost:7777`
2. Navigate to **Audit Workflow** tab
3. Upload Excel file
4. Select audit type:
   - 🔢 **Audit Keuangan** — ROA, ROE, DER analysis + anomaly detection
   - 🛡️ **Audit SPI** — COSO Framework 5-component evaluation
   - 📊 **Audit Kinerja** — Performance scoring A/B/C/D/E
5. Click **Jalankan Audit**
6. View real-time charts + download Excel report

### Via CLI
```bash
# Interactive menu
python template_master.py

# Direct execution
python template_master.py keuangan
python template_master.py spi
python template_master.py kinerja
```

### Via API
```bash
curl -X POST -F "file=@data.xlsx" http://localhost:7777/api/audit/upload

curl -X POST http://localhost:7777/api/audit/run \
  -H "Content-Type: application/json" \
  -d '{"jenis":"keuangan","filename":"data.xlsx"}'
```

---

## 🧪 Testing

```bash
pytest tests/ -v
```

Current: **22 passed, 1 skipped**

---

## 🔧 Maintenance

```bash
# Database optimization (vacuum + indexes + archive)
python scripts/db_maintenance.py

# Cleanup redundant scripts (dry run first)
python sanitizer.py --dry-run
python sanitizer.py
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `docs/reference/ARCHITECTURE.md` | System architecture & data flow |
| `docs/planning/ROADMAP_48H.md` | 48-hour development roadmap |
| `README_AUDIT_AI.md` | Audit toolkit detailed guide |
| `README_UNIFIED.md` | Control panel guide |
| `MEMORY.md` | Long-term project memory |

---

## ⚠️ Red Lines

1. **Never share sensitive assignment data publicly**
2. **All audit data stays local** unless explicitly exported
3. **Git-ignore all .db files, .gguf models, and logs**

---

## 🏗️ Built By

**panomr5973** (panomr5973) — Auditor at Government Audit Agency Indonesia

---

*KUERA: Kumpulan Utilitas Evaluasi & Riset Audit*
