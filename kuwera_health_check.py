#!/usr/bin/env python
"""
KUWERA AI - Health Check & Status Monitor
Check status of all services and models
"""

import json
import sqlite3
import urllib.request
from pathlib import Path
from datetime import datetime

def check_web_server():
    """Check if web server is running"""
    try:
        with urllib.request.urlopen('http://localhost:5000/api/stats', timeout=5) as response:
            data = json.loads(response.read())
            return {
                'status': 'running',
                'interactions': data.get('total_interactions', 0),
                'avg_rating': data.get('average_rating', 0)
            }
    except Exception as e:
        return {'status': 'stopped', 'error': str(e)}

def check_model_registry():
    """Check model registry status"""
    registry_file = Path("models/llm/model_registry_active.json")
    if registry_file.exists():
        with open(registry_file) as f:
            registry = json.load(f)
        return {
            'total_models': registry.get('total_models', 0),
            'total_size_gb': registry.get('total_size_gb', 0),
            'indonesian': len(registry.get('indonesian_models', [])),
            'multilingual': len(registry.get('multilingual_models', [])),
            'coding': len(registry.get('coding_models', [])),
            'bartowski': len(registry.get('bartowski_models', []))
        }
    return None

def check_databases():
    """Check database status"""
    data_dir = Path("data")
    databases = {}
    
    # Evolution database
    evo_db = data_dir / "kuera_evolution.db"
    if evo_db.exists():
        try:
            conn = sqlite3.connect(str(evo_db))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM interactions")
            count = cursor.fetchone()[0]
            conn.close()
            databases['evolution'] = {'status': 'ok', 'interactions': count}
        except:
            databases['evolution'] = {'status': 'error'}
    else:
        databases['evolution'] = {'status': 'not_found'}
    
    # Knowledge base
    kb_file = data_dir / "knowledge_base.json"
    if kb_file.exists():
        with open(kb_file) as f:
            kb = json.load(f)
        databases['knowledge'] = {
            'status': 'ok',
            'facts': kb.get('facts_learned', 0),
            'topics': len(kb.get('topics', []))
        }
    else:
        databases['knowledge'] = {'status': 'not_found'}
    
    return databases

def check_autostart_status():
    """Check autostart service status"""
    status_file = Path("logs/kuwera/status.json")
    if status_file.exists():
        with open(status_file) as f:
            return json.load(f)
    return None

def print_health_report():
    """Print comprehensive health report"""
    print("="*70)
    print("  KUWERA AI - HEALTH CHECK")
    print("="*70)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Web Server
    print("  🌐 WEB SERVER")
    print("  " + "-"*66)
    web_status = check_web_server()
    if web_status['status'] == 'running':
        print(f"  Status:     🟢 RUNNING")
        print(f"  URL:        http://localhost:5000")
        print(f"  Interactions: {web_status['interactions']}")
        print(f"  Avg Rating:   {web_status['avg_rating']:.2f}")
    else:
        print(f"  Status:     🔴 STOPPED")
        print(f"  Error:      {web_status.get('error', 'Unknown')}")
    print()
    
    # Models
    print("  🤖 MODELS")
    print("  " + "-"*66)
    registry = check_model_registry()
    if registry:
        print(f"  Total Models:   {registry['total_models']}")
        print(f"  Total Size:     {registry['total_size_gb']:.2f} GB")
        print(f"  Indonesian:     {registry['indonesian']}")
        print(f"  Multilingual:   {registry['multilingual']}")
        print(f"  Coding:         {registry['coding']}")
        print(f"  Bartowski:      {registry['bartowski']}")
    else:
        print("  Registry not found!")
    print()
    
    # Databases
    print("  💾 DATABASES")
    print("  " + "-"*66)
    databases = check_databases()
    for name, status in databases.items():
        if status['status'] == 'ok':
            if name == 'evolution':
                print(f"  {name:12} 🟢 {status['interactions']} interactions")
            elif name == 'knowledge':
                print(f"  {name:12} 🟢 {status['facts']} facts, {status['topics']} topics")
        elif status['status'] == 'not_found':
            print(f"  {name:12} 🟡 Not found (will be created)")
        else:
            print(f"  {name:12} 🔴 Error")
    print()
    
    # Autostart Status
    print("  🚀 AUTOSTART SERVICE")
    print("  " + "-"*66)
    autostart = check_autostart_status()
    if autostart:
        print(f"  Last Update:    {autostart.get('timestamp', 'N/A')}")
        services = autostart.get('services', {})
        for svc, info in services.items():
            status = info.get('status', 'unknown')
            icon = '🟢' if status == 'running' else '🔴' if status == 'failed' else '⚪'
            print(f"  {svc:12} {icon} {status}")
        
        summary = autostart.get('summary', {})
        print(f"\n  Running: {summary.get('running', 0)}/{summary.get('total', 0)} services")
    else:
        print("  Autostart not running")
    print()
    
    # Summary
    print("="*70)
    print("  QUICK COMMANDS")
    print("="*70)
    print("  Start services:  python kuwera_autostart.py")
    print("  Web Interface:   http://localhost:5000")
    print("  View logs:       logs/kuwera/")
    print("="*70)

if __name__ == "__main__":
    print_health_report()
