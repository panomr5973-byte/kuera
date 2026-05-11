# KUERA 48-Hour Roadmap

> Created: 2026-05-11 | Status: Phase 8 Active

---

## Hour 0-4: System Stabilization ✅ DONE

- [x] Git commit: Audit Workflow + Charts + DB Maintenance
- [x] Run `sanitizer.py` — archived 42 redundant scripts
- [x] Commit cleanup manifest
- [x] Create `src/core/logger_engine.py`
- [x] Integrate logger into `main.py`
- [x] Write `docs/reference/ARCHITECTURE.md`

**Deliverable:** Clean workspace with 2 commits, documented architecture.

---

## Hour 4-12: Consolidation (Day 1)

### API Consolidation
- [ ] Merge `app/api.py` + `app/real_api.py` + `app/real_api_v2.py` + `app/production_api.py` into single `src/web/api.py`
- [ ] Pick canonical API (FastAPI, `real_api_v2.py` as base — most robust)
- [ ] Update `config/services.yaml` to point to new unified API
- [ ] Test: `pytest tests/test_api.py`

### Dashboard Consolidation
- [ ] Merge `app/dashboard.py` + `app/dashboard_v2.py` logic into `src/web/dashboard.py` (or deprecate Streamlit)
- [ ] Update `start_dashboard.py` to use unified dashboard
- [ ] Remove redundant app/ files after migration

### Audit Toolkit Modularization
- [ ] Create `src/audit/` package
- [ ] Move `audit_toolkit.py`, `template_audit_spi.py`, `template_audit_kinerja.py` to `src/audit/`
- [ ] Update all imports (`template_master.py`, `audit_workflow.py`, `audit_connector.py`)
- [ ] Add `src/audit/__init__.py` with re-exports for backward compatibility

**Deliverable:** Single API entry point, single dashboard, audit toolkit in src/.

---

## Hour 12-24: Integration (Day 1 - Night)

### FORSA BUMDes Bridge
- [ ] Create `src/data/forsa_connector.py`
- [ ] Bridge to WSL `~/ai-audit/forsa_scripts/`
- [ ] Add API endpoint: `/api/audit/forsa/status`
- [ ] Add API endpoint: `/api/audit/forsa/run`
- [ ] Update Control Panel with FORSA tab

### Export Pipeline
- [ ] Add PDF export directly from web UI (endpoint + button)
- [ ] Add PNG chart export (Chart.js `toDataURL()`)
- [ ] Batch processing: multiple Excel files in one run

### Test Coverage
- [ ] Add tests for consolidated API
- [ ] Add tests for FORSA connector
- [ ] Target: 30+ tests, >80% coverage for src/

**Deliverable:** FORSA integration, export pipeline, expanded test suite.

---

## Hour 24-36: Hardening (Day 2)

### Security & Compliance
- [ ] PII detection in uploaded files (`personal_ai/privacy_guard.py`)
- [ ] Auto-redact sensitive fields before analysis
- [ ] Audit trail: log every analysis run to `data/audit_log.db`
- [ ] Role-based access (viewer vs auditor vs admin)

### Performance
- [ ] SQLite connection pooling for kuera_database.db
- [ ] Cache chart data (LRU) to avoid regeneration
- [ ] Lazy-load model registry (currently loads all at startup)
- [ ] Compress old logs automatically

### Error Handling
- [ ] Graceful degradation if pandas/matplotlib not installed
- [ ] Retry logic for file uploads
- [ ] User-friendly error messages in UI (not just stack traces)

**Deliverable:** Secure, fast, resilient system.

---

## Hour 36-48: Polish & Release (Day 2)

### Documentation
- [ ] Fill `docs/api/` with OpenAPI/Swagger references
- [ ] Fill `docs/reference/` with data model diagrams
- [ ] Update `README.md` root to reflect actual KUERA (not generic template)
- [ ] Create `docs/guides/AUDIT_WORKFLOW.md` — step-by-step for auditors

### Deployment
- [ ] Dockerize: `docker-compose.yml` with all services
- [ ] Environment-based config (dev/staging/prod)
- [ ] Auto-start script for Windows (`start_kuera.bat` yang clean)

### Final Commit
- [ ] `git tag v3.2.0 "Phase 8 Complete: Systematic Growth"`
- [ ] Push to GitHub
- [ ] Update MEMORY.md with Phase 8 summary

**Deliverable:** v3.2.0 release, documented, Dockerized, deployed.

---

## Success Criteria

| Metric | Current | Target (48h) |
|--------|---------|--------------|
| Root .py files | ~60 | < 20 |
| Test count | 23 | 35+ |
| API endpoints | 12 | 18 |
| Documentation files | 15 | 25 |
| Git commits | 13 | 20+ |
| Docker support | ❌ | ✅ |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| API merge breaks existing clients | Keep old endpoints as redirects for 1 release cycle |
| Audit toolkit import errors after move | `__init__.py` re-exports + thorough tests |
| FORSA bridge fails on WSL | Fallback to manual upload + status check |
| Docker image too large (models/) | Exclude models/ via .dockerignore; mount as volume |

---

## Daily Standup Template

```markdown
## Standup YYYY-MM-DD

### Yesterday
- 

### Today
- 

### Blockers
- 

### Commits
- 
```

Write this to `memory/standup_YYYY-MM-DD.md` each day.
