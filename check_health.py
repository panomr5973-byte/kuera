#!/usr/bin/env python
"""
Health Check - Monitor aplikasi yang sedang berjalan
"""

import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime

def check_api():
    """Check API health"""
    try:
        r = requests.get("http://localhost:8000/health", timeout=5)
        data = r.json()
        return {
            'status': 'running',
            'interactions': data.get('total_interactions', 0),
            'model': data.get('production_model', 'None'),
            'satisfaction': data.get('feedback_stats', {}).get('satisfaction_rate', 0)
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def check_scheduler():
    """Check if scheduler is running"""
    status_file = Path("logs/startup/status.json")
    if status_file.exists():
        with open(status_file) as f:
            data = json.load(f)
        return {
            'status': data.get('status', 'unknown'),
            'started_at': data.get('started_at', 'unknown')
        }
    return {'status': 'not_found'}

def check_database():
    """Check database stats"""
    try:
        import sqlite3
        conn = sqlite3.connect("logs/feedback/self_improve.db")
        
        cursor = conn.execute("SELECT COUNT(*) FROM interactions")
        total = cursor.fetchone()[0]
        
        cursor = conn.execute("""
            SELECT COUNT(*) FROM interactions 
            WHERE user_feedback IS NOT NULL
        """)
        with_feedback = cursor.fetchone()[0]
        
        cursor = conn.execute("""
            SELECT COUNT(*) FROM interactions 
            WHERE timestamp > datetime('now', '-1 day')
        """)
        today = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'status': 'ok',
            'total_interactions': total,
            'with_feedback': with_feedback,
            'today': today
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def main():
    print("="*60)
    print("HEALTH CHECK - Self-Evolving AI")
    print("="*60)
    print(f"Time: {datetime.now()}")
    
    # Check API
    print("\n[API] API Server:")
    api = check_api()
    if api['status'] == 'running':
        print(f"  [OK] Running")
        print(f"       Interactions: {api['interactions']}")
        print(f"       Model: {api['model']}")
        print(f"       Satisfaction: {api['satisfaction']:.1f}%")
    else:
        print(f"  [FAIL] {api.get('error', 'Not running')}")
    
    # Check Scheduler
    print("\n[SCHEDULER] Scheduler:")
    sched = check_scheduler()
    print(f"  [{sched['status'].upper()}] Started: {sched.get('started_at', 'N/A')}")
    
    # Check Database
    print("\n[DB] Database:")
    db = check_database()
    if db['status'] == 'ok':
        print(f"  [OK] Total: {db['total_interactions']} interactions")
        print(f"       With feedback: {db['with_feedback']}")
        print(f"       Today: {db['today']}")
    else:
        print(f"  [FAIL] {db.get('error', 'Error')}")
    
    # Quick Actions
    print("\n" + "="*60)
    print("QUICK ACTIONS:")
    print("="*60)
    print("1. View Dashboard: streamlit run app/dashboard.py")
    print("2. View Logs:     type logs\\startup\\*.log")
    print("3. Test API:      curl http://localhost:8000/health")
    print("4. Stop All:      Task Manager -> End Python tasks")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
