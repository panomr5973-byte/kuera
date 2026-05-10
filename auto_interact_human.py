#!/usr/bin/env python
"""
Auto Interact Human-like - Simulasi 50 interaksi dengan kepribadian manusia
Mood: Bosan, Penasaran, Marah, Sabar, Santai
"""

import requests
import time
import random
import sys
from datetime import datetime

API_URL = "http://localhost:8000"

# Kepribadian dengan karakteristik berbeda
PERSONALITIES = {
    'bosan': {
        'name': '[BOSAN] Bosan',
        'desc': 'Tidak fokus, feedback asal-asalan, cepat lelah',
        'accuracy': 0.4,  # 40% benar (asal pilih)
        'delay_range': (0.1, 0.5),  # Cepat, tidak mikir
        'messages': [
            "Ya sudahlah...", "Hmm... whatever", "Cepat dong...",
            "Boring...", "Udah belum?", "Skip ah..."
        ]
    },
    'penasaran': {
        'name': '[CARI] Penasaran',
        'desc': 'Ingin tahu, cek hasil detail, banyak tanya',
        'accuracy': 0.8,  # 80% benar (perhatikan detail)
        'delay_range': (1.5, 3.0),  # Lama, diperhatikan
        'messages': [
            "Menarik!", "Coba cek lagi...", "Kenapa ya?",
            "Oh gitu...", "Coba yang lain...", "Bisa dijelaskan?"
        ]
    },
    'marah': {
        'name': '[MARAH] Marah',
        'desc': 'Frustrasi, banyak komplain, sering salah tekan',
        'accuracy': 0.3,  # 30% benar (emosi, gak fokus)
        'delay_range': (0.2, 0.8),  # Cepat, buru-buru
        'messages': [
            "Salah lagi!", "Gimana sih!", "Kok gini terus!",
            "Gak jelas!", "Parah!", "Fix dong!"
        ]
    },
    'sabar': {
        'name': '[SABAR] Sabar',
        'desc': 'Tenang, pikir dulu, balanced feedback',
        'accuracy': 0.75,  # 75% benar (hati-hati)
        'delay_range': (1.0, 2.0),  # Normal, dipertimbangkan
        'messages': [
            "Oke, saya coba...", "Hmm, coba ini...", "Bisa jadi...",
            "Mari kita lihat...", "Santai saja...", "Bagus nih..."
        ]
    },
    'santai': {
        'name': '[SANTAI] Santai',
        'desc': 'Easy going, positive vibes, gak terlalu serius',
        'accuracy': 0.85,  # 85% benar (positif thinking)
        'delay_range': (0.8, 1.5),  # Santai
        'messages': [
            "Mantap!", "Nice!", "Oke lah ya...",
            "Chill aja...", "Gampang ini...", "Lanjut bos..."
        ]
    }
}

class HumanLikeInteraction:
    def __init__(self):
        self.session = requests.Session()
        self.stats = {p: {'total': 0, 'correct': 0} for p in PERSONALITIES}
        self.interaction_log = []
        
    def check_api(self):
        try:
            r = self.session.get(f"{API_URL}/health", timeout=3)
            return r.status_code == 200
        except:
            return False
    
    def get_current_personality(self, interaction_num):
        """
        Rotasi kepribadian setiap 10 interaksi
        Atau random jika diinginkan
        """
        personalities = list(PERSONALITIES.keys())
        
        # Setiap 10 interaksi, ganti kepribadian
        idx = (interaction_num // 10) % len(personalities)
        
        # Atau bisa juga random
        # idx = random.randint(0, len(personalities) - 1)
        
        return personalities[idx]
    
    def simulate_interaction(self, personality_key, interaction_num):
        """Satu interaksi dengan kepribadian tertentu"""
        p = PERSONALITIES[personality_key]
        
        print(f"\n{'='*60}")
        print(f"  Interaksi #{interaction_num} | {p['name']}")
        print(f"  Mood: {p['desc']}")
        print(f"{'='*60}")
        
        # Delay sesuai kepribadian
        delay = random.uniform(*p['delay_range'])
        print(f"  [Thinking... {delay:.1f}s] {random.choice(p['messages'])}")
        time.sleep(delay)
        
        try:
            # 1. Get sample
            print(f"  [Action] Mengambil data...")
            r = self.session.get(f"{API_URL}/sample", timeout=5)
            sample = r.json()
            
            # 2. Predict
            print(f"  [Action] AI sedang berpikir...")
            r = self.session.post(
                f"{API_URL}/predict",
                json={
                    "model_id": "best_model_logistic_regression",
                    "input_data": sample,
                    "session_id": f"human_{personality_key}_{interaction_num}"
                },
                timeout=5
            )
            
            if r.status_code != 200:
                print(f"  [ERROR] Predict failed: {r.text}")
                return False
            
            result = r.json()
            prediction = result.get('prediction')
            confidence = result.get('confidence', 0.5)
            interaction_id = result.get('interaction_id')
            
            print(f"\n  [RESULT]")
            print(f"    Prediction: {prediction}")
            print(f"    Confidence: {confidence*100:.1f}%")
            
            # 3. Feedback dengan "pemikiran" manusia
            print(f"\n  [Persona Thinking...]")
            
            # Logic feedback berdasarkan kepribadian + confidence
            is_correct = self.decide_feedback(personality_key, confidence)
            feedback = 1 if is_correct else 0
            
            # Human-like reasoning
            reasoning = self.get_reasoning(personality_key, is_correct, confidence)
            print(f"    {reasoning}")
            
            # Submit feedback
            if interaction_id:
                r = self.session.post(
                    f"{API_URL}/feedback",
                    json={
                        "interaction_id": interaction_id,
                        "feedback": feedback,
                        "reason": reasoning if feedback == 0 else None
                    },
                    timeout=3
                )
                
                if r.status_code == 200:
                    print(f"    [OK] Feedback: {'Benar' if feedback == 1 else 'Salah'}")
                else:
                    print(f"    [ERROR] Feedback failed")
            
            # Update stats
            self.stats[personality_key]['total'] += 1
            if is_correct:
                self.stats[personality_key]['correct'] += 1
            
            # Log
            self.interaction_log.append({
                'num': interaction_num,
                'personality': personality_key,
                'prediction': prediction,
                'confidence': confidence,
                'feedback': feedback,
                'correct': is_correct
            })
            
            return True
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            return False
    
    def decide_feedback(self, personality, confidence):
        """
        Decide if feedback is correct or not based on personality
        """
        p = PERSONALITIES[personality]
        base_accuracy = p['accuracy']
        
        # Modifikasi berdasarkan confidence AI
        # High confidence AI → lebih mungkin user setuju (kecuali marah)
        if personality == 'marah':
            # Orang marah: sering tidak setuju meski AI confident
            return random.random() < (base_accuracy - confidence * 0.2)
        elif personality == 'penasaran':
            # Orang penasaran: cek detail, lebih akurat
            return random.random() < (base_accuracy + confidence * 0.1)
        elif personality == 'bosan':
            # Orang bosan: asal pilih
            return random.random() < base_accuracy
        elif personality == 'santai':
            # Orang santai: ikut flow, positif
            return random.random() < (base_accuracy + 0.1)
        else:  # sabar
            return random.random() < base_accuracy
    
    def get_reasoning(self, personality, is_correct, confidence):
        """Generate human-like reasoning"""
        p = PERSONALITIES[personality]
        
        if is_correct:
            if personality == 'santai':
                return random.choice(["Oke lah", "Mantap", "Nice!"])
            elif personality == 'penasaran':
                return random.choice(["Sesuai teori", "Logis", "Make sense"])
            elif personality == 'sabar':
                return random.choice(["Ini benar", "Setuju", "Pass"])
            elif personality == 'bosan':
                return random.choice(["Ya udah", "Ok", "Skip"])
            else:  # marah
                return random.choice(["Akhirnya", "Bener juga", "Hmph ok"])
        else:
            if personality == 'marah':
                return random.choice(["Salah!", "Gimana sih!", "Fix dong!"])
            elif personality == 'penasaran':
                return random.choice(["Kayaknya salah", "Ngga yakin", "Coba dicek"])
            elif personality == 'sabar':
                return random.choice(["Kayaknya beda", "Ngga match", "Kurang tepat"])
            elif personality == 'bosan':
                return random.choice(["Salah deh", "Skip", "Ngga bener"])
            else:  # santai
                return random.choice(["Ngga cocok", "Salah nih", "Oke deh salah"])
    
    def run(self, total_interactions=50):
        """Run human-like simulation"""
        print("="*70)
        print("  HUMAN-LIKE AUTO INTERACTION")
        print("  50 Interaksi dengan Kepribadian: Bosan, Penasaran, Marah, Sabar, Santai")
        print("="*70)
        
        if not self.check_api():
            print("\n  [ERROR] API tidak berjalan!")
            print("  Jalankan: python app/real_api_v2.py")
            return
        
        print("\n  [OK] API connected!")
        print("\n  Kepribadian yang akan muncul:")
        for key, p in PERSONALITIES.items():
            print(f"    {p['name']}: {p['desc']}")
        print("")
        
        success_count = 0
        
        for i in range(1, total_interactions + 1):
            personality = self.get_current_personality(i)
            success = self.simulate_interaction(personality, i)
            
            if success:
                success_count += 1
            
            # Progress setiap 10
            if i % 10 == 0:
                print(f"\n{'='*70}")
                print(f"  PROGRESS: {i}/{total_interactions} interaksi")
                print(f"{'='*70}")
        
        # Final Report
        self.print_final_report(success_count, total_interactions)
    
    def print_final_report(self, success_count, total):
        print("\n" + "="*70)
        print("  LAPORAN AKHIR - SIMULASI MANUSIA")
        print("="*70)
        
        print(f"\n  Total Interactions: {success_count}/{total}")
        
        print(f"\n  Breakdown per Kepribadian:")
        for key, stats in self.stats.items():
            p = PERSONALITIES[key]
            if stats['total'] > 0:
                accuracy = (stats['correct'] / stats['total']) * 100
                print(f"    {p['name']}: {stats['correct']}/{stats['total']} benar ({accuracy:.0f}%)")
        
        # Overall stats
        total_correct = sum(s['correct'] for s in self.stats.values())
        total_done = sum(s['total'] for s in self.stats.values())
        if total_done > 0:
            overall = (total_correct / total_done) * 100
            print(f"\n  Overall Accuracy: {total_correct}/{total_done} ({overall:.0f}%)")
        
        print(f"\n  Mood Summary:")
        print(f"    - Bosan: Asal-asalan, gak fokus")
        print(f"    - Penasaran: Detail-oriented, banyak tanya")
        print(f"    - Marah: Frustrasi, banyak komplain")
        print(f"    - Sabar: Balanced, hati-hati")
        print(f"    - Santai: Easy-going, positif")
        
        print("\n" + "="*70)
        print("  Data ini akan digunakan untuk training ulang AI!")
        print("="*70)


def main():
    sim = HumanLikeInteraction()
    sim.run(total_interactions=50)


if __name__ == "__main__":
    main()
