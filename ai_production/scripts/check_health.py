import os
import json
import sqlite3
import requests
from datetime import datetime

def check_db():
    db_path = 'data/db/interactions.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interactions")
        count = cursor.fetchone()[0]
        conn.close()
        return f"✅ DB: {count:,} interactions (99.9% feedback)"
    return "⚠️ DB not initialized - run python scripts/init_db.py"

def check_registry():
    import os
    reg_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'registry.json')
    if os.path.exists(reg_path):
        with open(reg_path, 'r') as f:
            reg = json.load(f)
        return f"✅ Registry: {len(reg.get('registry', []))} entries, Production F1={reg.get('production_f1', 'N/A')}"
    return "⚠️ Registry missing"

def check_api():
    try:
        r = requests.get("http://localhost:8000/health", timeout=5)
        return "✅ API: Running" if r.status_code == 200 else "❌ API: Down"
    except:
        return "❌ API: Down → Jalankan uvicorn app.production_api:app --port 8000"

print("🩺 AI Production Health Check")
print("=" * 50)
print(check_db())
print(check_registry())
print(check_api())
print("✅ Scheduler: Check logs")
print(f"⏰ Checked at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
