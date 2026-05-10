#!/usr/bin/env python
"""
Auto Interact - Generate interaksi otomatis untuk demo
Bisa dijalankan background untuk mengisi database
"""

import requests
import time
import random
import argparse
from datetime import datetime

API_URL = "http://localhost:8000"

class AutoInteract:
    def __init__(self):
        self.session = requests.Session()
        self.stats = {
            'total': 0,
            'correct': 0,
            'incorrect': 0
        }
    
    def check_api(self):
        try:
            r = self.session.get(f"{API_URL}/health", timeout=3)
            return r.status_code == 200
        except:
            return False
    
    def interact_once(self):
        """Satu siklus interaksi"""
        try:
            # 1. Get sample
            r = self.session.get(f"{API_URL}/sample", timeout=5)
            sample = r.json()
            
            # 2. Predict
            r = self.session.post(
                f"{API_URL}/predict",
                json={
                    "model_id": "best_model_logistic_regression",
                    "input_data": sample,
                    "session_id": f"auto_{datetime.now().timestamp()}"
                },
                timeout=5
            )
            
            if r.status_code != 200:
                return False
            
            result = r.json()
            interaction_id = result.get('interaction_id')
            confidence = result.get('confidence', 0.5)
            
            # 3. Auto feedback (70% correct untuk demo)
            is_correct = random.random() < 0.7
            feedback = 1 if is_correct else 0
            
            if interaction_id:
                self.session.post(
                    f"{API_URL}/feedback",
                    json={
                        "interaction_id": interaction_id,
                        "feedback": feedback,
                        "reason": "Auto-generated" if not is_correct else None
                    },
                    timeout=3
                )
            
            # Update stats
            self.stats['total'] += 1
            if is_correct:
                self.stats['correct'] += 1
            else:
                self.stats['incorrect'] += 1
            
            return True
            
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    def run(self, count=50, delay=1.0, verbose=True):
        """Run auto interact"""
        print(f"\n{'='*60}")
        print(f"  AUTO INTERACT - {count} interaksi")
        print(f"{'='*60}")
        
        if not self.check_api():
            print("[ERROR] API tidak berjalan!")
            print("Jalankan: python app/real_api_v2.py")
            return
        
        print(f"[OK] API connected")
        print(f"[INFO] Target: {count} interaksi")
        print(f"[INFO] Delay: {delay}s per interaksi")
        print(f"[INFO] Estimasi waktu: {count * delay / 60:.1f} menit")
        print(f"{'='*60}\n")
        
        for i in range(count):
            success = self.interact_once()
            
            if success:
                if verbose and (i + 1) % 10 == 0:
                    acc = (self.stats['correct'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
                    print(f"  Progress: {i+1}/{count} | Accuracy: {acc:.0f}%")
            else:
                print(f"  [FAIL] Interaksi {i+1} gagal")
            
            if i < count - 1:
                time.sleep(delay)
        
        # Summary
        print(f"\n{'='*60}")
        print(f"  SELESAI!")
        print(f"{'='*60}")
        print(f"  Total: {self.stats['total']}")
        print(f"  Correct: {self.stats['correct']}")
        print(f"  Incorrect: {self.stats['incorrect']}")
        if self.stats['total'] > 0:
            print(f"  Accuracy: {self.stats['correct']/self.stats['total']*100:.1f}%")
        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Auto Interact with AI")
    parser.add_argument("-n", "--count", type=int, default=50, help="Jumlah interaksi")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Delay antar interaksi (detik)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode (less output)")
    
    args = parser.parse_args()
    
    auto = AutoInteract()
    auto.run(count=args.count, delay=args.delay, verbose=not args.quiet)


if __name__ == "__main__":
    main()
