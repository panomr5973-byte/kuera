# AI Production Evolution (80% Evolved - Production Ready!)

## Quick Start (Local)
1. cd ai_production
2. setup.bat (one-time venv/pip)
3. run_production.bat (API + monitor)

**Endpoints:**
- `http://localhost:8000/health` 
- `http://localhost:8000/registry`
- `curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"text\": \"AI suka Indonesia\"}` → Positive
- WS: `ws://localhost:8000/ws/evolution` realtime updates
- Docs: http://localhost:8000/docs

## Docker
cd docker
docker build -t ai-production .
docker run -p 8000:8000 ai-production

## Auto on Boot (Windows)
run_auto_boot.bat

## Scripts
- python scripts/check_evolution.py → 80% status
- python scripts/watch_evolution.py → Live monitor
- python scripts/check_health.py → Health
- python scripts/init_db.py → DB
- python scripts/generate_dummy_models.py → Train GB (F1~0.67 Indonesian data)

**Status:** 3.5M DB Indonesia demografi, GB F1=0.673, realtime inference/WS/scheduler!

Kuera TODO: 10/10 🎯
