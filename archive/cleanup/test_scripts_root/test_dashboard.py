#!/usr/bin/env python
"""
Test Dashboard - Validasi halaman Feedback & Improvement
"""
import sys
import streamlit as st

# Mock test untuk validasi import
def test_imports():
    print("[TEST] Testing imports...")
    try:
        import pandas as pd
        import numpy as np
        import plotly.express as px
        import plotly.graph_objects as go
        print("[OK] Core libraries imported")
        
        from self_evolving.data_collector import DataCollector
        from self_evolving.retrainer import AutoRetrain, RetrainConfig
        print("[OK] Self-evolving components imported")
        
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_database():
    print("\n[TEST] Testing database connection...")
    try:
        import sqlite3
        from pathlib import Path
        
        db_path = "logs/feedback/self_improve.db"
        if Path(db_path).exists():
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT COUNT(*) FROM interactions")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"[OK] Database connected. Total interactions: {count}")
        else:
            print(f"[WARN] Database not found at {db_path}")
        return True
    except Exception as e:
        print(f"[FAIL] Database error: {e}")
        return False

def test_model_registry():
    print("\n[TEST] Testing model registry...")
    try:
        import json
        from pathlib import Path
        
        registry_path = Path("models/model_registry.json")
        if registry_path.exists():
            with open(registry_path) as f:
                registry = json.load(f)
            print(f"[OK] Registry loaded. Models: {len(registry.get('models', []))}")
        else:
            print("[WARN] Registry not found. Run retraining first.")
        return True
    except Exception as e:
        print(f"[FAIL] Registry error: {e}")
        return False

def test_dashboard_page():
    print("\n[TEST] Testing dashboard page validation...")
    try:
        with open("app/dashboard.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for new page
        if "Feedback & Improvement" in content:
            print("[OK] Feedback page found in navigation")
        else:
            print("[FAIL] Feedback page not found")
            return False
        
        # Check for key components
        checks = [
            ("DataCollector import", "from self_evolving.data_collector import DataCollector"),
            ("Statistics section", "📈 Interaction Statistics"),
            ("API Endpoints", "📚 API Endpoints"),
            ("Test API button", "🧪 Run Test"),
        ]
        
        for name, keyword in checks:
            if keyword in content:
                print(f"[OK] {name} found")
            else:
                print(f"[WARN] {name} not found")
        
        return True
    except Exception as e:
        print(f"[FAIL] Dashboard test error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("DASHBOARD TEST SUITE")
    print("="*60)
    
    results = [
        test_imports(),
        test_database(),
        test_model_registry(),
        test_dashboard_page(),
    ]
    
    print("\n" + "="*60)
    if all(results):
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nTo run dashboard:")
        print("  streamlit run app/dashboard.py")
        print("\nThen navigate to: [Feedback & Improvement] page")
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)
