# Long-Term Memory — KUERA AI Workspace

> Curated wisdom, not raw logs. Updated: 2026-05-10

---

## About This Workspace

This is `D:\workspace\ai_core\AI-Project`, home to KUERA AI — a local multi-model AI system built by panomr (panomr5973), an auditor at Government Audit Agency. The project has gone through 7 phases of evolution in ~5 weeks (2 Apr – 5 May 2026).

---

## The 7 Phases (Compressed)

1. **Self-Evolving Experiments** — Auto-training, feedback loops, ML pipeline (scikit-learn).
2. **Enterprise Stack** — Personal AI, safety guards, monitoring, evaluation modules.
3. **Audit Toolkit** — Excel processor, anomaly detection, PDF export for Government Audit Agency workflows.
4. **WorldBank + Local LLM** — Economic data integration + ctransformers GGUF inference.
5. **Model Frenzy** — Downloaded 12 models (29.45 GB). Created 18 redundant download scripts.
6. **Persona & Cleanup** — Gave AI a character ("Protective Chuunibyou"). Archived 20 old files.
7. **Unified Desktop** — Single control panel (port 7777) to manage all services. WebSocket gateway (port 18789).
8. **Audit Workflow Integration** — Unified audit dashboard (Keuangan + SPI + Kinerja), real anomaly detection (IQR/Z-Score/Benford), DB maintenance scripts.

---

## Key Architectural Decisions

- **Local-first**: All LLMs run locally via ctransformers (CPU, no GPU).
- **GGUF format**: Q4_K_M quantization for efficiency.
- **Indonesian focus**: Qwen2.5 series as primary models.
- **Flask-based UI**: Embedded HTML strings in Python — quick but hard to maintain.
- **SQLite for everything**: Logs, memory, evolution state, worldbank data — all SQLite.

---

## Critical Patterns to Avoid

### The Fix Spiral
When a bug appears, **edit the existing file**. Do not create `fix_*.py`, `*_v2.py`, or duplicate variants. This project already has 13 fix scripts and multiple versioned files that are technical debt.

### The Download Obsession
One download manager is enough. The project accumulated 8 download strategies for the same task. Consolidate into `src/models/download_manager.py` if needed.

### The Chat Proliferation
Every chat iteration should refine existing code, not spawn new files. There were 9 chat interfaces before consolidation.

---

## What Works Now

| Component | File | Status |
|-----------|------|--------|

| **Audit Workflow** | `src/data/audit_workflow.py` | ✅ **NEW** — 3 jenis audit via UI |
| **Anomaly Detection** | `audit_toolkit.py` | ✅ **NEW** — IQR + Z-Score + Benford |
| **DB Maintenance** | `scripts/db_maintenance.py` | ✅ **NEW** — Vacuum + indexes |
| **Real-time Charts** | `src/web/templates/control_panel.html` | ✅ **NEW** — Chart.js visualisasi audit |
| Tests | `tests/` | ✅ 22 passed, 1 skipped |

---

## Recent Changes (2026-05-11)

### Bug Fixes
- `template_master.py`: Fixed broken `audit_toolkit_complete` import → `audit_toolkit`
- `app/production_api.py`: Fixed `start_time` scoping bug (used before defined)
- `app/dashboard_v2.py`: Fixed syntax error (newline inside if expression)

### New Features
- **Unified Audit Workflow**: Upload Excel → pilih jenis audit → hasil langsung di dashboard
- **Real Anomaly Detection**: IQR outliers, Z-Score extremes, Benford's Law first-digit analysis
- **API Endpoints**: `/api/audit/templates`, `/api/audit/run`, `/api/audit/upload`
- **DB Maintenance**: `scripts/db_maintenance.py` — vacuum, analyze, create indexes, archive old data
- **HEARTBEAT.md**: Periodic health checks configured

### Test Coverage
- Added `tests/test_audit_workflow.py` (8 tests)
- Total: 18 passed, 1 skipped

---

## What Works Now (Legacy)

| Component | File | Status |
|-----------|------|--------|
| Unified Control Panel | `main.py` + `src/` | ✅ Active (port 7777) |
| WebSocket Gateway | `gateway_server.py` | ✅ Active (port 18789) |
| WorldBank Data | `data/worldbank_indonesia.db` | ✅ 212 records |
| International Data | `data/international_data.db` | ✅ 10 currencies + crypto |
| Memory System | `memory/` | ✅ Retroactive fill complete |
| Git | `.git/` | ✅ Initialized 2026-05-10 |
| Terabox Backup | `scripts/terabox/` | ✅ Ready (needs cookies) |
| Modularized src/ | `src/core/`, `src/web/`, `src/utils/`, `src/data/` | ✅ Complete |

---

## What Needs Attention

1. **Port conflict**: `kuera_admin` moved to 5001. `kuera_web_v2` stays at 5000.
2. **Memory gap filled**: 23-day hiatus (12 Apr – 5 May) now documented.
3. **Log rotation**: Large logs compressed. `data/kuera_database.db` is 2.36 GB — monitor growth.
4. **HEARTBEAT.md empty**: No periodic tasks configured.
5. **`.sixth/skills` empty**: Skill system never used.
6. **Terabox backup**: Scripts ready but requires manual cookie extraction from browser.

---

## User Context (panomr)

- Works at Government Audit Agency (Indonesian government audit agency).
- Username: panomr5973. Timezone: GMT+7 (Jakarta/WIB).
- **Red line**: Never share sensitive assignment data or audit results publicly.
- Tool stack: MS Office, LibreOffice, Google Workspace, Canva, Python, Playwright.
- Currently working on: Forsa BUMDes automation (WSL Ubuntu + Playwright).
- Preferred communication: Conversational Indonesian with professional directness.

---

## Ritme Kerja yang Lebih Baik

Based on observation:
- **10-day sprint** (2-11 Apr) → 99 files, chaos, burnout.
- **23-day break** → reflection, then 3 focused files.
- **Better rhythm**: 3 days active, 1 day review, 1 day rest. Repeat.

---

## Last Words

This project is a study in builder's trap: too many ideas, too little consolidation. The Unified Desktop (Fase 7) is not elegant architecture — it's survival. The real growth will come from disciplined cleanup, not new features.

**Terabox Backup Target** (~27 GB):
- `models/llm/*.gguf` → ~25 GB (12 models)
- `data/kuera_database.db` → ~2.3 GB
- `data/*.db` → ~200 KB

*"Don't build more. Build better."*
