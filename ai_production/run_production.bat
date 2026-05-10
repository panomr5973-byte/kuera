@echo off
cd /d c:/AI-Project/ai_production
call venv\Scripts\activate.bat
start /B python scripts/watch_evolution.py
start python -m uvicorn app.production_api:app --host 0.0.0.0 --port 8000 --reload
echo 🚀 Production API + Monitor running!
echo Health: http://localhost:8000/health
echo Dashboard: http://localhost:8000/static/dashboard.html
start http://localhost:8000/static/dashboard.html
echo Docs: http://localhost:8000/docs
pause
