# KUERA Architecture Reference

> Version: 3.1 | Last Updated: 2026-05-11

## Philosophy

**Local-first. Modular. Audit-ready.**

KUERA is built as a local AI workstation for government audit workflows (Government Audit Agency). Every component runs on-premise. No data leaves the machine unless explicitly exported.

---

## Directory Structure

```
AI-Project/
├── main.py                      # Unified entry point (port 7777)
├── gateway_server.py            # WebSocket gateway (port 18789)
├── config/
│   ├── settings.yaml            # App config (ports, paths)
│   └── services.yaml            # Service definitions
├── src/                         # Active codebase (23 Python modules)
│   ├── core/                    # Process orchestration
│   │   ├── process_manager.py   # Subprocess lifecycle + health probes
│   │   ├── service_registry.py  # Typed YAML config loader
│   │   └── logger_engine.py     # Memory injection (daily logs)
│   ├── web/                     # Flask dashboard + REST API
│   │   ├── dashboard.py         # Control panel routes
│   │   └── templates/
│   │       └── control_panel.html  # Dark-themed UI + Chart.js
│   ├── data/                    # Data connectors & pipelines
│   │   ├── audit_workflow.py    # Unified audit orchestrator
│   │   ├── audit_connector.py   # API wrapper for audit toolkit
│   │   ├── worldbank_connector.py  # World Bank SQLite API
│   │   ├── pipeline.py          # ML data pipeline
│   │   └── preprocessing.py     # Data cleaning stubs
│   ├── models/                  # Model registry & training
│   │   ├── registry.py          # Active model list
│   │   └── train.py             # Training stubs
│   ├── utils/                   # Shared utilities
│   │   ├── config.py            # Settings & ServiceRegistry classes
│   │   └── logger.py            # File + console logging
│   ├── evaluation/              # Metrics (minimal)
│   ├── monitoring/              # System monitoring (minimal)
│   ├── deployment/              # Empty stub
│   ├── memory/                  # Empty stub (planned)
│   └── persona/                 # Empty stub (planned)
├── app/                         # Legacy API variants (cleanup pending)
│   ├── production_api.py        # FastAPI v2.0.0 (port 8000)
│   ├── real_api_v2.py           # FastAPI v2.1.0 (port 8001)
│   ├── dashboard_v2.py          # Streamlit dashboard (port 8501)
│   └── api.py / app.py          # Minimal stubs
├── admin_panel/                 # Flask admin UI (port 5001)
├── audit_toolkit.py             # Core: Excel processor + anomaly detection
├── template_audit_spi.py        # SPI audit (COSO framework)
├── template_audit_kinerja.py    # Kinerja audit (scoring A/B/C/D/E)
├── template_master.py           # CLI menu for all 3 audits
├── tests/                       # pytest suite (23 tests)
├── scripts/                     # Operational scripts
│   ├── db_maintenance.py        # SQLite vacuum + indexes
│   ├── terabox/                 # Cloud backup scripts
│   └── tailscale/               # Network tunnel scripts
├── data/                        # Databases & uploads (4.75 GB)
│   ├── kuera_database.db        # Main app DB (~2.3 GB)
│   ├── worldbank_indonesia.db   # Economic indicators
│   ├── international_data.db    # Global economy data
│   └── uploads/                 # Excel files for audit
├── models/llm/                  # GGUF models (~29 GB)
├── memory/                      # Daily logs (.md files)
├── docs/                        # Documentation
├── archive/                     # Cleanup archive
│   └── cleanup/                 # 42 redundant scripts (manifest included)
└── archive_incomplete/          # Gitignored — early experiments
```

---

## Active Ports

| Port | Service | Entry Point | Status |
|------|---------|-------------|--------|
| 7777 | **Control Panel** | `main.py` | ✅ Primary |
| 18789 | WebSocket Gateway | `gateway_server.py` | ✅ Active |
| 8000 | Production API | `start_api.py` → `app/production_api.py` | ⏹️ Stopped |
| 8001 | Real API v2 | `app/real_api_v2.py` | ⏹️ Stopped |
| 5000 | Web Server v2 | `kuwera_web_server_v2.py` | ⏹️ Stopped |
| 5001 | Admin Panel | `admin_panel/start_admin.py` | ⏹️ Stopped |
| 8501 | Streamlit Dashboard | `start_dashboard.py` → `app/dashboard_v2.py` | ⏹️ Stopped |

> **Note:** All secondary services default to `auto_start: false`. Start them from the Control Panel or manually.

---

## Audit Workflow Architecture

```
User uploads Excel
        ↓
Control Panel (Flask) — /api/audit/upload
        ↓
audit_connector.py — analyze_excel()
        ↓
audit_workflow.py — run_audit(jenis, filepath)
        ↓
┌─────────────┬──────────────┬──────────────┐
│  Keuangan   │     SPI      │   Kinerja    │
│  (audit_    │ (template_   │ (template_   │
│  toolkit)   │ audit_spi)   │ audit_kinerja)│
└─────────────┴──────────────┴──────────────┘
        ↓
generate_chart_data() — Chart.js JSON
        ↓
Control Panel renders charts + text results
        ↓
Export: Excel + PDF + PNG
```

---

## Anomaly Detection

Three methods active in `audit_toolkit.py`:

1. **IQR (Interquartile Range)** — Flags outliers beyond 1.5× IQR
2. **Z-Score** — Flags values with |z| > 3 (99.7% rule)
3. **Benford's Law** — First-digit frequency analysis for fraud detection (χ² test)

---

## Data Flow

```
Raw Data (Excel/CSV)
        ↓
src/data/pipeline.py — Clean → Encode → Scale → Split
        ↓
Processed Data (data/processed/*.csv)
        ↓
Model Training (src/models/train.py)
        ↓
Models (models/llm/*.gguf, models/*.pkl)
        ↓
Inference APIs (app/real_api_v2.py)
        ↓
Dashboard / Control Panel
```

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **SQLite for everything** | Zero-config, portable, audit-friendly |
| **Flask Control Panel** | Single-file HTML, no build step, fast iteration |
| **Chart.js CDN** | No npm/webpack, instant charts |
| **Lazy imports** | Heavy deps (pandas, matplotlib) loaded on-demand |
| **Git archive cleanup** | Preserve history without cluttering workspace |

---

## Anti-Patterns (Documented & Enforced)

1. **Fix Spiral** → Edit existing files. No `fix_*.py`, no `*_v2.py`.
2. **Download Obsession** → One download manager is enough.
3. **Chat Proliferation** → Refine existing code, don't spawn new files.

---

## Planned (Not Yet Implemented)

- `src/memory/` — Structured memory storage beyond daily .md files
- `src/persona/` — Persona engine integration
- `src/deployment/` — Docker & production deployment scripts
- FORSA BUMDes connector (WSL bridge)
- Supabase/PostgreSQL cloud backup
