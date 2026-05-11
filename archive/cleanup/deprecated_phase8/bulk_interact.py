#!/usr/bin/env python
"""
Bulk Interact - 1000 interaksi cepat untuk trigger evolusi
Mode: Fast, minimal delay, batch processing
"""

import requests
import time
import random
from datetime import datetime

API_URL = "http://localhost:8000"

class BulkInteraction:
    def __init__(self):
        self.session = requests.Session()
        self.stats = {'total': 0, 'success': 0, 'failed': 0}
        
    def check_api(self):
        try:
            r = self.session.get(f"{API_URL}/health", timeout=3)
            return r.status_code == 200
        except:
            return False
    
    def interact_batch(self, batch_size=100):
        """Process a batch of interactions"""
        success = 0
        
        for i in range(batch_size):
            try:
                # Predict
                r = self.session.post(
                    f"{API_URL}/predict",
                    json={
                        "model_id": "best_model_logistic_regression",
                        "session_id": f"bulk_{datetime.now().timestamp()}"
                    },
                    timeout=5
                )
                
                if r.status_code == 200:
                    data = r.json()
                    interaction_id = data.get('interaction_id')
                    
                    # Random feedback (70% positive, 30% negative)
                    if interaction_id:
                        feedback = 1 if random.random() < 0.7 else 0
                        self.session.post(
                            f"{API_URL}/feedback",
                            json={
                                "interaction_id": interaction_id,
                                "feedback": feedback
                            },
                            timeout=2
                        )
                        success += 1
                        
            except Exception as e:
                pass
            
            # Minimal delay
            time.sleep(0.05)
        
        return success
    
    def run(self, target=1000):
        print("="*70)
        print(f"  BULK INTERACTION - {target} interaksi cepat")
        print("="*70)
        
        if not self.check_api():
            print("[ERROR] API tidak berjalan!")
            return
        
        print("[OK] API connected!")
        print(f"[INFO] Target: {target} interaksi")
        print(f"[INFO] Mode: Cepat (delay 0.05s)")
        print(f"[INFO] Estimasi: ~{target * 0.06 / 60:.1f} menit")
        print("="*70)
        
        start_time = time.time()
        batch_size = 100
        total_success = 0
        
        for batch_num in range(target // batch_size):
            print(f"\n  Batch {batch_num + 1}/{(target // batch_size)}...")
            
            success = self.interact_batch(batch_size)
            total_success += success
            
            elapsed = time.time() - start_time
            rate = (batch_num + 1) * batch_size / elapsed if elapsed > 0 else 0
            remaining = (target - (batch_num + 1) * batch_size) / rate if rate > 0 else 0
            
            print(f"    Progress: {(batch_num + 1) * batch_size}/{target}")
            print(f"    Success: {total_success}")
            print(f"    Rate: {rate:.1f} interactions/sec")
            print(f"    ETA: {remaining:.0f}s")
        
        # Summary
        elapsed = time.time() - start_time
        print("\n" + "="*70)
        print("  SELESAI!")
        print("="*70)
        print(f"  Total: {target}")
        print(f"  Success: {total_success}")
        print(f"  Failed: {target - total_success}")
        print(f"  Time: {elapsed:.1f}s")
        print(f"  Rate: {target/elapsed:.1f} interactions/sec")
        print("="*70)


if __name__ == "__main__":
    bulk = BulkInteraction()
    bulk.run(target=1000)
