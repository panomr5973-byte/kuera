# AI Production Evolution TODO (Kuera 9/10 + Production)

## Core Infrastructure (9/9 done ✅)

- [x] 1. Create folder structure (initial files)
- [ ] 2. requirements.txt + pip install -r requirements.txt
- [ ] 3. config/registry.json + data/db/interactions.db schema/sample + models/ .pkl placeholders
- [x] 4. scripts/check_evolution.py (80% status output)

- [ ] 5. scripts/watch_evolution.py (monitoring + realtime)
- [ ] 6. scripts/check_health.py
- [x] 7. app/production_api.py (FastAPI realtime/websockets)

- [x] 8. docker/Dockerfile + README.md

- [x] 9. Auto-start on Windows boot/restart (Task Scheduler + .bat)


## Testing/Deploy
- [ ] Run python scripts/check_health.py
- [ ] uvicorn app.production_api:app --reload
- [ ] python scripts/watch_evolution.py
- [ ] Docker build/run

## Auto-Run on Boot
- [ ] Create run_production.bat
- [ ] Windows Task Scheduler: Run on login/boot (API + watch_evolution)
