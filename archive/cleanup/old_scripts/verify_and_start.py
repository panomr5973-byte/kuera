#!/usr/bin/env python
"""
Verify & Start - One command to check and launch everything
Bisa dijalankan manual atau otomatis
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    return version.major >= 3 and version.minor >= 10

def check_venv():
    """Check virtual environment"""
    venv_python = Path("ai_env/Scripts/python.exe")
    if venv_python.exists():
        print(f"[OK] Virtual environment: {venv_python}")
        return True
    else:
        print("[FAIL] Virtual environment not found!")
        print("       Run: python -m venv ai_env")
        return False

def check_dependencies():
    """Check required packages"""
    required = [
        'fastapi', 'uvicorn', 'pandas', 'sklearn',
        'streamlit', 'schedule', 'requests'
    ]
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
            print(f"[OK] {pkg}")
        except ImportError:
            print(f"[MISSING] {pkg}")
            missing.append(pkg)
    
    if missing:
        print(f"\n[INSTALL] pip install {' '.join(missing)}")
        return False
    return True

def check_database():
    """Check/create database"""
    db_path = Path("logs/feedback/self_improve.db")
    if db_path.exists():
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM interactions")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"[OK] Database exists ({count} interactions)")
    else:
        print("[INFO] Database will be created on first run")
    return True

def check_models():
    """Check model directory"""
    models_dir = Path("models")
    if models_dir.exists():
        pkl_files = list(models_dir.glob("*.pkl"))
        print(f"[OK] Models directory ({len(pkl_files)} .pkl files)")
        
        # Check registry
        registry = models_dir / "model_registry.json"
        if registry.exists():
            with open(registry) as f:
                data = json.load(f)
            print(f"[OK] Model registry ({len(data.get('models', []))} models)")
    else:
        print("[INFO] Models directory will be created")
    return True

def start_services():
    """Start all services"""
    print_section("STARTING SERVICES")
    
    import threading
    import time
    
    def run_api():
        subprocess.run([sys.executable, "run_self_evolving.py"])
    
    def run_scheduler():
        time.sleep(3)  # Wait for API
        subprocess.run([sys.executable, "start_scheduler.py"])
    
    # Start threads
    api_thread = threading.Thread(target=run_api, daemon=True)
    sched_thread = threading.Thread(target=run_scheduler, daemon=True)
    
    api_thread.start()
    sched_thread.start()
    
    print("[OK] API Server: http://localhost:8000")
    print("[OK] Scheduler: Running in background")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP] Shutting down...")

def main():
    print_section("VERIFY & START - Self-Evolving AI")
    print(f"Time: {datetime.now()}")
    
    # Run checks
    print_section("ENVIRONMENT CHECK")
    
    checks = [
        ("Python", check_python()),
        ("Virtual Env", check_venv()),
        ("Dependencies", check_dependencies()),
        ("Database", check_database()),
        ("Models", check_models()),
    ]
    
    # Summary
    print_section("CHECK SUMMARY")
    all_passed = all(result for _, result in checks)
    
    for name, result in checks:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")
    
    if all_passed:
        print("\n[OK] All checks passed!")
        
        # Ask to start
        response = input("\nStart services now? [Y/n]: ").strip().lower()
        if response in ('', 'y', 'yes'):
            start_services()
        else:
            print("[INFO] Not starting. Run manually with:")
            print("       python run_self_evolving.py")
            print("       python start_scheduler.py")
    else:
        print("\n[FAIL] Some checks failed. Please fix before starting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
