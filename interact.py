#!/usr/bin/env python
"""
Interactive CLI - Berinteraksi langsung dengan AI
Cara paling mudah untuk chat dengan AI dan kasih feedback
"""

import requests
import json
import random
from datetime import datetime

API_URL = "http://localhost:8000"

class AIInteraction:
    def __init__(self):
        self.session = requests.Session()
        self.interaction_history = []
        
    def check_connection(self):
        """Cek apakah API berjalan"""
        try:
            r = self.session.get(f"{API_URL}/health", timeout=3)
            return r.status_code == 200
        except:
            return False
    
    def get_sample_data(self):
        """Ambil sample data untuk prediksi"""
        try:
            r = self.session.get(f"{API_URL}/sample", timeout=5)
            return r.json()
        except:
            return None
    
    def predict(self, model_id="best_model_logistic_regression"):
        """Lakukan prediksi"""
        # Ambil sample data
        sample = self.get_sample_data()
        if not sample:
            print("[ERROR] Tidak bisa ambil sample data")
            return None
        
        # Prediksi
        try:
            r = self.session.post(
                f"{API_URL}/predict",
                json={
                    "model_id": model_id,
                    "input_data": sample,
                    "session_id": f"interactive_{datetime.now().timestamp()}"
                },
                timeout=5
            )
            
            if r.status_code == 200:
                result = r.json()
                return result
            else:
                print(f"[ERROR] {r.text}")
                return None
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return None
    
    def give_feedback(self, interaction_id, is_correct):
        """Beri feedback"""
        try:
            r = self.session.post(
                f"{API_URL}/feedback",
                json={
                    "interaction_id": interaction_id,
                    "feedback": 1 if is_correct else 0,
                    "reason": "User feedback" if not is_correct else None
                },
                timeout=3
            )
            return r.status_code == 200
        except:
            return False
    
    def print_banner(self):
        print("\n" + "="*60)
        print("  [AI] INTERAKSI LANGSUNG DENGAN AI")
        print("="*60)
        print("\n  Cara kerja:")
        print("  1. AI membuat prediksi dari data real")
        print("  2. Anda nilai apakah prediksi benar/salah")
        print("  3. Feedback Anda digunakan untuk improve AI!")
        print("="*60)
    
    def interactive_mode(self):
        """Mode interaktif"""
        self.print_banner()
        
        # Cek koneksi
        if not self.check_connection():
            print("\n  [ERROR] AI tidak berjalan!")
            print("  Jalankan dulu: python app/real_api_v2.py")
            return
        
        print("\n  [OK] AI terhubung!")
        
        count = 0
        correct_count = 0
        
        while True:
            print(f"\n{'='*60}")
            print(f"  Interaksi #{count + 1}")
            print(f"{'='*60}")
            
            # Prediksi
            print("\n  [AI] Sedang menganalisis data...")
            result = self.predict()
            
            if not result:
                print("  [ERROR] Prediksi gagal")
                retry = input("\n  Coba lagi? (y/n): ").lower()
                if retry != 'y':
                    break
                continue
            
            # Tampilkan hasil
            print(f"\n  [HASIL] HASIL PREDIKSI:")
            print(f"     Prediction: {result['prediction']} ({'Class 1' if result['prediction'] == 1 else 'Class 0'})")
            print(f"     Confidence: {result['confidence']*100:.1f}%")
            print(f"     Model: {result['model_used']}")
            
            # Feedback
            print(f"\n  [TANYA] Menurut Anda, prediksi ini:")
            print(f"     [1] Benar [OK]")
            print(f"     [2] Salah")
            print(f"     [3] Lewati")
            print(f"     [0] Selesai")
            
            choice = input("\n  Pilih (0-3): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.give_feedback(result['interaction_id'], True)
                correct_count += 1
                print("  [OK] Feedback tersimpan: [OK] Benar")
            elif choice == '2':
                self.give_feedback(result['interaction_id'], False)
                print("  [OK] Feedback tersimpan: [X] Salah")
            elif choice == '3':
                print("  [SKIP] Dilewati")
            
            count += 1
            
            # Stats
            if count > 0:
                accuracy = (correct_count / count) * 100
                print(f"\n  [STATS] Stats: {correct_count}/{count} benar ({accuracy:.0f}%)")
            
            # Lanjut?
            if count % 5 == 0:
                cont = input("\n  Lanjut interaksi? (y/n): ").lower()
                if cont != 'y':
                    break
        
        # Summary
        print("\n" + "="*60)
        print("  RINGKASAN SESSION")
        print("="*60)
        print(f"  Total interaksi: {count}")
        print(f"  Feedback benar: {correct_count}")
        print(f"  Feedback salah: {count - correct_count}")
        if count > 0:
            print(f"  Accuracy: {(correct_count/count)*100:.1f}%")
        print("\n  Terima kasih! Feedback Anda membantu AI berkembang!")
        print("="*60)


def main():
    ai = AIInteraction()
    ai.interactive_mode()


if __name__ == "__main__":
    main()
