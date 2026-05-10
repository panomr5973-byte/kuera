#!/usr/bin/env python
"""
Demo Loop - Generate 50+ interactions untuk trigger retraining
Jalankan setelah API berjalan: python demo_loop.py
"""
import requests
import time
import random

BASE_URL = "http://localhost:8000"

def test_queries():
    """Sample queries untuk demo"""
    return [
        "Apa itu machine learning?",
        "Bagaimana cara kerja AI?",
        "Jelaskan neural network",
        "Apa bedanya supervised dan unsupervised learning?",
        "Bagaimana AI bisa belajar sendiri?",
        "Apa itu deep learning?",
        "Bagaimana cara membuat chatbot?",
        "Apa itu natural language processing?",
        "Jelaskan computer vision",
        "Bagaimana AI digunakan dalam bisnis?",
    ]

def run_demo(n_interactions=50):
    print("="*60)
    print("DEMO LOOP - Self-Evolving AI")
    print("="*60)
    print(f"Generating {n_interactions} interactions...")
    print()
    
    queries = test_queries()
    
    for i in range(n_interactions):
        query = random.choice(queries)
        
        # 1. Chat
        try:
            resp = requests.post(
                f"{BASE_URL}/chat",
                json={"query": query, "session_id": f"demo_user"},
                timeout=10
            )
            data = resp.json()
            interaction_id = data['interaction_id']
            
            print(f"[{i+1}/{n_interactions}] Q: {query[:40]}... ID:{interaction_id}")
            
            # 2. Random feedback (70% positive)
            feedback = 1 if random.random() < 0.7 else 0
            reason = "Good answer" if feedback == 1 else "Not relevant"
            
            requests.post(
                f"{BASE_URL}/feedback",
                json={
                    "interaction_id": interaction_id,
                    "feedback": feedback,
                    "reason": reason
                },
                timeout=5
            )
            
            print(f"         Feedback: {'[OK]' if feedback == 1 else '[BAD]'}")
            
        except Exception as e:
            print(f"[{i+1}/{n_interactions}] Error: {e}")
        
        time.sleep(0.5)  # Be nice to the server
    
    print()
    print("="*60)
    print("DONE! Check health to see results:")
    print("  python check_health.py")
    print()
    print("Next steps:")
    print("1. Wait for scheduler to detect (check every hour)")
    print("2. Or trigger manually: POST /admin/retrain")
    print("3. Check new models: ls models/*.pkl")
    print("="*60)

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    run_demo(n)
