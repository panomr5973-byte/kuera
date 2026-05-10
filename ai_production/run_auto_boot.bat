@echo off
schtasks /delete /tn "AI-Evolution-Production" /f >nul 2>&1
/tr "\"c:/AI-Project/ai_production/python -m uvicorn app.production_api:app --host 0.0.0.0 --port 8000 --reload\"" 
echo ✅ Auto-boot task created: Runs production on login/restart
echo Check: schtasks /query /tn "AI-Evolution-Production"
pause
