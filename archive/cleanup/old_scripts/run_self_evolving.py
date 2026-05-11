#!/usr/bin/env python
"""
Launcher untuk Self-Evolving AI App
Menjalankan aplikasi AI yang dapat belajar dan berkembang mandiri

Usage:
    python run_self_evolving.py           # Start API server
    python run_self_evolving.py --test    # Run tests only
    python run_self_evolving.py --schedule # Start scheduler (background)
"""

import argparse
import sys
import time
import requests
import subprocess
import threading


def test_api(base_url="http://localhost:8000"):
    """Test Self-Evolving API"""
    print("="*60)
    print("TESTING SELF-EVOLVING AI APP")
    print("="*60)
    
    # 1. Health check
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        status = r.json()
        print(f"[OK] Status: {status['status']}")
        print(f"[OK] Model: {status['production_model']}")
        print(f"[OK] Interactions: {status['total_interactions']}")
        print(f"[OK] Feedback: {status['feedback_stats']}")
    except Exception as e:
        print(f"[FAIL] Health check: {e}")
        return False
    
    # 2. Chat test
    try:
        r = requests.post(
            f"{base_url}/chat",
            json={"query": "Halo, apa kabar?", "session_id": "test_001"},
            timeout=10
        )
        resp = r.json()
        print(f"\n[OK] Chat response: {resp['response'][:50]}...")
        print(f"[OK] Model used: {resp['model_used']}")
        print(f"[OK] Confidence: {resp['confidence']}")
        print(f"[OK] Interaction ID: {resp['interaction_id']}")
        
        interaction_id = resp['interaction_id']
    except Exception as e:
        print(f"[FAIL] Chat: {e}")
        return False
    
    # 3. Feedback test
    try:
        r = requests.post(
            f"{base_url}/feedback",
            json={"interaction_id": interaction_id, "feedback": 1, "reason": "Good response"},
            timeout=5
        )
        print(f"\n[OK] Feedback submitted: {r.json()['status']}")
    except Exception as e:
        print(f"[FAIL] Feedback: {e}")
    
    # 4. Admin stats
    try:
        r = requests.get(f"{base_url}/admin/stats", timeout=5)
        stats = r.json()
        print(f"\n[OK] Stats: {stats['interactions_24h']} interactions in 24h")
    except Exception as e:
        print(f"[FAIL] Stats: {e}")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED!")
    print("="*60)
    print(f"API Docs: {base_url}/docs")
    return True


def start_scheduler():
    """Start background scheduler untuk auto-retrain"""
    print("Starting auto-retrain scheduler...")
    from self_evolving.retrainer import run_scheduler_forever
    run_scheduler_forever()


def main():
    parser = argparse.ArgumentParser(description="Self-Evolving AI App")
    parser.add_argument("--test", action="store_true", help="Run tests only")
    parser.add_argument("--schedule", action="store_true", help="Start scheduler")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    args = parser.parse_args()
    
    if args.schedule:
        start_scheduler()
        return
    
    if args.test:
        test_api(f"http://localhost:{args.port}")
        return
    
    # Start server
    print("="*60)
    print("SELF-EVOLVING AI APP")
    print("="*60)
    print(f"Server akan berjalan di: http://localhost:{args.port}")
    print("Tekan CTRL+C untuk berhenti")
    print("="*60)
    
    import uvicorn
    from self_evolving.app import app
    
    # Start test thread setelah server jalan
    def delayed_test():
        time.sleep(3)
        print("\n[Auto-Test] Running tests...")
        test_api(f"http://localhost:{args.port}")
    
    tester = threading.Thread(target=delayed_test, daemon=True)
    tester.start()
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
