# KUERA AI — Master Execution Plan

**Disusun oleh:** Multi-Stakeholder Council (Planner + Architect + Coder + Analyst + Business Manager + User)  
**Tanggal:** 2026-05-10  
**Status:** Phase 0 In Progress  
**Target:** Transformasi dari "Mode Survival" ke "Mode Growth" dalam 4 fase terukur.

---

## Executive Summary (Business Manager Perspective)

Proyek KUERA AI memiliki **aset berharga** (12 model lokal, data WorldBank, audit toolkit, persona system) tapi terkubur dalam **technical debt** (99 file root, HTML embedded 759 baris, port conflict, tanpa test). 

**ROI Prioritas:**
1. **High Impact, Low Risk**: Modularisasi + Entry point unifikasi (memudahkan user, mengurangi bug)
2. **High Impact, Medium Risk**: Refactor ProcessManager + pisah HTML (meningkatkan maintainability)
3. **Medium Impact, Low Risk**: Test suite + Config terpusat (meningkatkan confidence)
4. **High Impact, High Risk**: Audit toolkit integration (menambah value bisnis)

**Jangan buat fitur baru sampai fondasi rapi.**

---

## Phase 0: Foundation (Hari Ini — 1-2 Jam)

### Goal
Struktur direktori yang jelas, entry point tunggal, dan config terpusat.

### Deliverables
- [x] `src/` directory structure
- [x] `main.py` — entry point TUNGGAL
- [x] `config/settings.yaml` — konfigurasi terpusat
- [x] `config/services.yaml` — definisi service
- [ ] `requirements-clean.txt` — dependency yang benar-benar dipakai

### Acceptance Criteria
- User bisa jalankan `python main.py` dan mendapatkan behavior yang sama dengan `python kuera_unified_desktop.py`
- Tidak ada file baru di root selain `main.py`

---

## Phase 1: Modularisasi Core (Hari Ini — 2-3 Jam)

### Goal
Pisahkan `kuera_unified_desktop.py` (759 baris) menjadi modul-modul terpisah.

### Deliverables
- [ ] `src/core/process_manager.py` — ProcessManager class (murni Python, tanpa Flask)
- [ ] `src/core/service_registry.py` — Definisi service dari `SERVICES` dict
- [ ] `src/web/dashboard.py` — Flask routes saja
- [ ] `src/web/templates/control_panel.html` — HTML terpisah (!)
- [ ] `src/utils/logger.py` — Unified logging setup

### Acceptance Criteria
- `kuera_unified_desktop.py` di-deprecated (diberi deprecation warning)
- `main.py` import dari `src/` 
- HTML tidak lagi embedded dalam string Python

---

## Phase 2: Test & Config (Besok — 1-2 Jam)

### Goal
Confidence bahwa sistem tidak rusak saat diubah.

### Deliverables
- [ ] `tests/test_process_manager.py` — Mock test untuk start/stop/restart
- [ ] `tests/test_service_registry.py` — Test load services dari YAML
- [ ] `tests/test_config.py` — Test config loading
- [ ] `pytest.ini` + GitHub Actions / local runner

### Acceptance Criteria
- `pytest tests/` pass minimal 80%
- Config bisa diubah tanpa edit kode

---

## Phase 3: Integration & Polish (Minggu Depan — 2-3 Jam)

### Goal
Hubungkan kembali fitur bisnis yang terbuang.

### Deliverables
- [ ] `src/data/audit_connector.py` — Hubungkan `audit_toolkit.py` ke Unified Desktop
- [ ] `src/data/worldbank_connector.py` — Query WorldBank dari dashboard
- [ ] Port conflict fix (5000 → 5001 untuk admin panel)
- [ ] `README.md` baru yang sesuai struktur

### Acceptance Criteria
- User bisa query data ekonomi Indonesia dari Control Panel
- Audit toolkit bisa dipanggil dari CLI `python main.py --mode audit`

---

## Phase 4: Growth Mode (Bulan Depan)

### Goal
Tambah value bisnis nyata untuk panomr.

### Deliverables
- [ ] Auto-generate laporan audit dari Excel upload
- [ ] Forsa BUMDes data integration (WSL bridge)
- [ ] Voice interface (Whisper local)
- [ ] Mobile-friendly dashboard

---

## Arsitektur Target

```
KUERA-PROJECT/
├── main.py                     # ← Entry point TUNGGAL
├── config/
│   ├── settings.yaml           # ← Config terpusat
│   └── services.yaml           # ← Service definitions
├── src/
│   ├── core/
│   │   ├── process_manager.py  # ← Process lifecycle
│   │   ├── orchestrator.py     # ← Main orchestrator
│   │   └── service_registry.py # ← Service definitions
│   ├── web/
│   │   ├── dashboard.py        # ← Flask routes
│   │   └── templates/
│   │       └── control_panel.html  # ← HTML terpisah!
│   ├── models/
│   │   ├── registry.py         # ← Model registry loader
│   │   └── downloader.py       # ← Unified download manager
│   ├── data/
│   │   ├── worldbank.py        # ← WorldBank queries
│   │   ├── international.py    # ← International data
│   │   └── audit_connector.py  # ← Audit toolkit bridge
│   ├── memory/
│   │   └── agent.py            # ← Auto-memory logging
│   ├── persona/
│   │   └── identity.py         # ← Persona & identity
│   └── utils/
│       ├── config.py           # ← Config loader
│       └── logger.py           # ← Unified logging
├── tests/
│   ├── test_process_manager.py
│   ├── test_service_registry.py
│   └── test_config.py
├── archive/                    # ← File lama (di-readonly)
├── data/                       # ← Database & uploads
├── models/llm/                 # ← .gguf files
└── memory/                     # ← Daily memory logs
```

---

## Decision Log

| # | Decision | Rationale | Stakeholder |
|---|----------|-----------|-------------|
| 1 | Gunakan `src/` layout | Python best practice, memudahkan import | System Analyst |
| 2 | YAML untuk config | Human-readable, bisa diedit tanpa buka kode | User |
| 3 | HTML terpisah dari Python | Maintainability, bisa edit UI tanpa sentuh logic | Coder |
| 4 | ProcessManager tetap threading | Cukup untuk use case ini, async = overkill | Architect |
| 5 | Jangan hapus file lama | Archive saja, user mungkin masih butuh referensi | Business Manager |
| 6 | pytest minimal | Lebih baik 3 test yang pass dari 30 test yang broken | Analyst |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Refactor merusak existing behavior | High | High | Buat wrapper, jangan hapus file lama. Test sebelum merge. |
| User bingung dengan struktur baru | Medium | Medium | Dokumentasi + entry point tunggal. |
| Port conflict belum terpecahkan | Medium | Medium | Fix di Phase 3 dengan config port. |
| Dependency missing di requirements | High | Medium | Scan import dari src/, bukan root. |

---

## Definition of Done (Phase 0-1)

```bash
# User harus bisa menjalankan ini tanpa error:
python main.py

# Dan mendapatkan behavior identik dengan:
python kuera_unified_desktop.py

# Plus ini:
pytest tests/ -q  # minimal 3 test pass
```

---

*Plan ini hidup. Update setiap milestone.*
