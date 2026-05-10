#!/usr/bin/env python
"""
MEGA SIMULATION - 1 Juta Interaksi dengan Demografi Lengkap
Simulasi populasi manusia dari seluruh dunia dengan:
- Semua gender
- Berbagai kelompok umur
- Kondisi sosial berbeda
- Emosi yang beragam
"""

import requests
import time
import random
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict
import threading
import sys

API_URL = "http://localhost:8001"

# ============================================================
# DEMOGRAFI LENGKAP MANUSIA
# ============================================================

@dataclass
class DemographicProfile:
    name: str
    weight: float  # Proporsi dalam populasi
    
# GENDER (World Bank 2023)
GENDERS = [
    ("Laki-laki", 50.4),
    ("Perempuan", 49.6),
    ("Non-biner", 0.05),
]

# KELOMPOK UMUR (World Population 2023)
AGE_GROUPS = [
    ("Anak (0-12)", 25.0, "curiosity_high", "attention_short"),
    ("Remaja (13-17)", 15.0, "rebellious", "tech_savvy"),
    ("Dewasa Muda (18-25)", 18.0, "energetic", "exploratory"),
    ("Dewasa (26-35)", 16.0, "career_focused", "stressed"),
    ("Dewasa Paruh Baya (36-50)", 14.0, "experienced", "cautious"),
    ("Pra-pensiun (51-60)", 7.0, "reflective", "patient"),
    ("Lansia (61-75)", 4.0, "wise", "slow"),
    ("Manula (75+)", 1.0, "traditional", "careful"),
]

# KONDISI SOSIAL
SOCIAL_CONDITIONS = [
    ("Pelajar", 15.0, "budget_limited", "curious"),
    ("Mahasiswa", 12.0, "budget_tight", "experimental"),
    ("Karyawan Swasta", 25.0, "time_limited", "practical"),
    ("PNS/BUMN", 8.0, "stable", "risk_averse"),
    ("Wiraswasta", 10.0, "busy", "decisive"),
    ("Profesional", 8.0, "demanding", "precise"),
    ("Ibu Rumah Tangga", 12.0, "multitasking", "patient"),
    ("Pensiunan", 5.0, "relaxed", "thorough"),
    ("Pengangguran", 3.0, "stressed", "frustrated"),
    ("Artis/Kreator", 2.0, "creative", "unpredictable"),
]

# STATUS EKONOMI
ECONOMIC_STATUS = [
    ("Miskin", 10.0, "price_sensitive", "careful"),
    ("Menengah Bawah", 25.0, "budget_conscious", "selective"),
    ("Menengah", 35.0, "balanced", "practical"),
    ("Menengah Atas", 22.0, "quality_focused", "demanding"),
    ("Kaya", 8.0, "premium_preference", "impatient"),
]

# KEADAAN EMOSIONAL
EMOTIONAL_STATES = [
    ("Bahagia", 20.0, 0.85, "positive", "fast"),
    ("Santai", 15.0, 0.80, "positive", "normal"),
    ("Netral", 18.0, 0.65, "neutral", "normal"),
    ("Cemas", 12.0, 0.50, "negative", "hesitant"),
    ("Stres", 10.0, 0.40, "negative", "impatient"),
    ("Marah", 8.0, 0.30, "negative", "fast"),
    ("Sedih", 7.0, 0.45, "negative", "slow"),
    ("Bosan", 5.0, 0.50, "neutral", "distracted"),
    ("Antusias", 3.0, 0.90, "positive", "engaged"),
    ("Frustrasi", 2.0, 0.35, "negative", "quick"),
]

# LOKASI GEOGRAFIS
REGIONS = [
    ("Jakarta", "urban", "fast_paced"),
    ("Surabaya", "urban", "moderate"),
    ("Bandung", "urban", "relaxed"),
    ("Yogyakarta", "college_town", "intellectual"),
    ("Bali", "tourist", "relaxed"),
    ("Medan", "urban", "business"),
    ("Makassar", "urban", "moderate"),
    ("Desa Jawa", "rural", "traditional"),
    ("Desa Sumatera", "rural", "conservative"),
    ("Papua", "remote", "slow"),
]

class MegaSimulator:
    def __init__(self, target=1_000_000):
        self.target = target
        self.session = requests.Session()
        self.stats = {
            'total': 0,
            'success': 0,
            'by_gender': {},
            'by_age': {},
            'by_emotion': {},
            'by_social': {},
        }
        self.start_time = time.time()
        self.lock = threading.Lock()
        
    def generate_persona(self) -> Dict:
        """Generate persona lengkap berdasarkan demografi real"""
        # Weighted random selection
        gender = random.choices([g[0] for g in GENDERS], weights=[g[1] for g in GENDERS])[0]
        age_group = random.choices([a[0] for a in AGE_GROUPS], weights=[a[1] for a in AGE_GROUPS])[0]
        social = random.choices([s[0] for s in SOCIAL_CONDITIONS], weights=[s[1] for s in SOCIAL_CONDITIONS])[0]
        economic = random.choices([e[0] for e in ECONOMIC_STATUS], weights=[e[1] for e in ECONOMIC_STATUS])[0]
        emotion = random.choices([e[0] for e in EMOTIONAL_STATES], weights=[e[1] for e in EMOTIONAL_STATES])[0]
        region = random.choice(REGIONS)
        
        # Calculate behavior modifiers
        emotion_data = next(e for e in EMOTIONAL_STATES if e[0] == emotion)
        accuracy = emotion_data[2]  # Base accuracy
        
        # Modifiers
        if age_group.startswith("Anak"):
            accuracy *= 0.7  # Anak kurang teliti
        elif age_group.startswith("Dewasa"):
            accuracy *= 1.0  # Dewasa standar
        elif age_group.startswith("Lansia"):
            accuracy *= 0.9  # Lansia lebih hati-hati
            
        if economic[0] == "Kaya":
            accuracy *= 0.8  # Kaya = lebih santai, kurang teliti
        elif economic[0] == "Miskin":
            accuracy *= 1.1  # Miskin = lebih careful
            
        # Clamp accuracy
        accuracy = max(0.1, min(0.95, accuracy))
        
        return {
            'gender': gender,
            'age_group': age_group,
            'social': social,
            'economic': economic,
            'emotion': emotion,
            'region': region[0],
            'region_type': region[1],
            'accuracy': accuracy,
            'speed': emotion_data[4],
        }
    
    def interact_single(self, persona: Dict, interaction_num: int) -> bool:
        """Satu interaksi dengan persona tertentu"""
        try:
            # Predict
            r = self.session.post(
                f"{API_URL}/predict",
                json={
                    "model_id": "best_model_logistic_regression",
                    "session_id": f"mega_{persona['region']}_{interaction_num}"
                },
                timeout=3
            )
            
            if r.status_code != 200:
                return False
                
            result = r.json()
            interaction_id = result.get('interaction_id')
            
            if not interaction_id:
                return False
            
            # Determine feedback based on persona accuracy
            is_correct = random.random() < persona['accuracy']
            feedback = 1 if is_correct else 0
            
            # Submit feedback
            self.session.post(
                f"{API_URL}/feedback",
                json={
                    "interaction_id": interaction_id,
                    "feedback": feedback,
                    "reason": f"{persona['emotion']}_{persona['social']}"
                },
                timeout=2
            )
            
            # Update stats
            with self.lock:
                self.stats['success'] += 1
                
                # By gender
                g = persona['gender']
                self.stats['by_gender'][g] = self.stats['by_gender'].get(g, 0) + 1
                
                # By age
                a = persona['age_group']
                self.stats['by_age'][a] = self.stats['by_age'].get(a, 0) + 1
                
                # By emotion
                e = persona['emotion']
                self.stats['by_emotion'][e] = self.stats['by_emotion'].get(e, 0) + 1
                
                # By social
                s = persona['social']
                self.stats['by_social'][s] = self.stats['by_social'].get(s, 0) + 1
            
            return True
            
        except Exception as e:
            return False
    
    def run_worker(self, worker_id: int, chunk_size: int):
        """Worker thread untuk batch interaksi"""
        for i in range(chunk_size):
            persona = self.generate_persona()
            success = self.interact_single(persona, worker_id * chunk_size + i)
            
            with self.lock:
                self.stats['total'] += 1
                
                # Progress every 1000
                if self.stats['total'] % 1000 == 0:
                    elapsed = time.time() - self.start_time
                    rate = self.stats['total'] / elapsed if elapsed > 0 else 0
                    remaining = (self.target - self.stats['total']) / rate if rate > 0 else 0
                    
                    print(f"\r  Progress: {self.stats['total']:,}/{self.target:,} "
                          f"({100*self.stats['total']/self.target:.1f}%) | "
                          f"Rate: {rate:.0f}/s | ETA: {remaining/60:.0f}m | "
                          f"Success: {self.stats['success']:,}", end='', flush=True)
            
            # Tiny delay to prevent overwhelming
            time.sleep(0.01)
    
    def run(self, num_workers=10):
        """Run mega simulation dengan multi-threading"""
        print("="*70)
        print(f"  MEGA SIMULATION - {self.target:,} INTERACTIONS")
        print("="*70)
        print("\n  Demografi:")
        print(f"    Gender: {len(GENDERS)} kategori")
        print(f"    Umur: {len(AGE_GROUPS)} kelompok")
        print(f"    Sosial: {len(SOCIAL_CONDITIONS)} kondisi")
        print(f"    Ekonomi: {len(ECONOMIC_STATUS)} level")
        print(f"    Emosi: {len(EMOTIONAL_STATES)} keadaan")
        print(f"    Lokasi: {len(REGIONS)} wilayah")
        print(f"\n  Workers: {num_workers}")
        print(f"  Estimasi: {self.target * 0.015 / 3600:.1f} jam")
        print("="*70)
        
        # Check API
        try:
            r = self.session.get(f"{API_URL}/health", timeout=3)
            if r.status_code != 200:
                print("[ERROR] API not running!")
                return
        except:
            print("[ERROR] Cannot connect to API!")
            return
        
        print("\n[OK] API connected!")
        print("\n[RUNNING] Memulai simulasi besar-besaran...")
        print("(Tekan Ctrl+C untuk berhenti)\n")
        
        # Calculate chunk per worker
        chunk_per_worker = self.target // num_workers
        
        # Start workers
        threads = []
        for i in range(num_workers):
            t = threading.Thread(target=self.run_worker, args=(i, chunk_per_worker))
            t.daemon = True
            threads.append(t)
            t.start()
        
        # Wait for completion
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED] Stopping...")
        
        # Final report
        self.print_report()
    
    def print_report(self):
        """Print comprehensive report"""
        elapsed = time.time() - self.start_time
        
        print("\n\n" + "="*70)
        print("  LAPORAN AKHIR - MEGA SIMULATION")
        print("="*70)
        
        print(f"\n  STATISTIK UTAMA:")
        print(f"    Total Interactions: {self.stats['total']:,}")
        print(f"    Successful: {self.stats['success']:,}")
        print(f"    Failed: {self.stats['total'] - self.stats['success']:,}")
        print(f"    Time: {elapsed/60:.1f} menit")
        print(f"    Rate: {self.stats['total']/elapsed:.0f} interactions/s")
        
        print(f"\n  BERDASARKAN GENDER:")
        for gender, count in sorted(self.stats['by_gender'].items(), key=lambda x: -x[1]):
            pct = count / self.stats['success'] * 100 if self.stats['success'] > 0 else 0
            print(f"    {gender}: {count:,} ({pct:.1f}%)")
        
        print(f"\n  BERDASARKAN UMUR:")
        for age, count in sorted(self.stats['by_age'].items(), key=lambda x: -x[1]):
            pct = count / self.stats['success'] * 100 if self.stats['success'] > 0 else 0
            print(f"    {age}: {count:,} ({pct:.1f}%)")
        
        print(f"\n  BERDASARKAN EMOSI:")
        for emotion, count in sorted(self.stats['by_emotion'].items(), key=lambda x: -x[1])[:5]:
            pct = count / self.stats['success'] * 100 if self.stats['success'] > 0 else 0
            print(f"    {emotion}: {count:,} ({pct:.1f}%)")
        
        print(f"\n  BERDASARKAN STATUS SOSIAL (Top 5):")
        for social, count in sorted(self.stats['by_social'].items(), key=lambda x: -x[1])[:5]:
            pct = count / self.stats['success'] * 100 if self.stats['success'] > 0 else 0
            print(f"    {social}: {count:,} ({pct:.1f}%)")
        
        print("\n" + "="*70)
        print("  Data tersimpan untuk training AI berikutnya!")
        print("="*70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1_000_000, help="Jumlah target interaksi")
    parser.add_argument("--workers", type=int, default=10, help="Jumlah worker threads")
    args = parser.parse_args()
    
    sim = MegaSimulator(target=args.target)
    sim.run(num_workers=args.workers)
