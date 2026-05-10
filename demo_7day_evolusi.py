#!/usr/bin/env python
"""
Demo 7 Hari Evolusi - Self-Evolving AI
Simulasi lengkap: Interact → Feedback → Retrain → Evolve

Usage:
    python demo_7day_evolusi.py --mode daily    # Simulasi 1 hari
    python demo_7day_evolusi.py --mode fast     # Speedup (1 jam = 1 minggu)
    python demo_7day_evolusi.py --monitor       # Monitor progress
"""

import argparse
import time
import json
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Simulate different user queries
QUERIES = [
    "Apa itu machine learning?",
    "Bagaimana cara kerja AI?",
    "Apa bedanya AI dan ML?",
    "Contoh implementasi AI di industri",
    "Cara belajar AI dari nol",
    "Tools AI yang populer",
    "Apa itu deep learning?",
    "Bagaimana AI belajar dari data?",
    "Etika dalam penggunaan AI",
    "Masa depan AI di Indonesia",
    "Apa itu neural network?",
    "Cara membuat model ML sederhana",
    "Apa itu data science?",
    "Bagaimana proses training model?",
    "Apa itu overfitting?",
    "Metrik evaluasi model ML",
    "Apa itu supervised learning?",
    "Perbedaan classification dan regression",
    "Apa itu unsupervised learning?",
    "Cara preprocessing data untuk ML",
]

class EvolutionDemo:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.interactions_log = []
        
    def check_api(self):
        """Check if API is running"""
        try:
            r = self.session.get(f"{self.base_url}/health", timeout=5)
            return r.status_code == 200
        except:
            return False
    
    def simulate_day(self, day_num, interactions_per_day=20):
        """
        Simulate one day of interactions
        
        Returns:
            dict: Statistics for the day
        """
        print(f"\n{'='*60}")
        print(f"  HARI {day_num}: SIMULASI {interactions_per_day} INTERAKSI")
        print(f"{'='*60}")
        
        stats = {
            'day': day_num,
            'interactions': 0,
            'positive': 0,
            'negative': 0,
            'avg_latency': 0
        }
        
        for i in range(interactions_per_day):
            # Random query
            query = random.choice(QUERIES)
            session_id = f"demo_day{day_num}_user{i}"
            
            try:
                # 1. Chat with AI
                start_time = time.time()
                r = self.session.post(
                    f"{self.base_url}/chat",
                    json={"query": query, "session_id": session_id},
                    timeout=10
                )
                latency = (time.time() - start_time) * 1000
                
                if r.status_code == 200:
                    data = r.json()
                    interaction_id = data['interaction_id']
                    
                    # 2. Random feedback (70% positive)
                    feedback = 1 if random.random() < 0.7 else 0
                    
                    self.session.post(
                        f"{self.base_url}/feedback",
                        json={
                            "interaction_id": interaction_id,
                            "feedback": feedback,
                            "reason": "Demo feedback" if feedback == 0 else None
                        },
                        timeout=5
                    )
                    
                    stats['interactions'] += 1
                    if feedback == 1:
                        stats['positive'] += 1
                    else:
                        stats['negative'] += 1
                    stats['avg_latency'] += latency
                    
                    # Progress bar
                    if (i + 1) % 5 == 0:
                        print(f"  Progress: {i+1}/{interactions_per_day} interactions")
                
            except Exception as e:
                print(f"  [ERROR] Interaction {i}: {e}")
                continue
            
            # Small delay to not overwhelm
            time.sleep(0.1)
        
        if stats['interactions'] > 0:
            stats['avg_latency'] /= stats['interactions']
        
        return stats
    
    def check_evolution(self):
        """Check current evolution status"""
        try:
            # Get health
            r = self.session.get(f"{self.base_url}/health", timeout=5)
            health = r.json()
            
            # Check models
            models_dir = Path("models")
            pkl_files = list(models_dir.glob("*.pkl"))
            
            # Check registry
            registry_path = models_dir / "model_registry.json"
            registry = {}
            if registry_path.exists():
                with open(registry_path) as f:
                    registry = json.load(f)
            
            return {
                'total_interactions': health.get('total_interactions', 0),
                'satisfaction': health.get('feedback_stats', {}).get('satisfaction_rate', 0),
                'production_model': health.get('production_model'),
                'model_count': len(pkl_files),
                'registry_models': len(registry.get('models', [])),
                'current_production': registry.get('current_production')
            }
        except Exception as e:
            print(f"[ERROR] Check evolution failed: {e}")
            return None
    
    def trigger_retrain(self):
        """Force trigger retraining"""
        try:
            r = self.session.post(
                f"{self.base_url}/admin/retrain",
                json={"force": True},
                timeout=30
            )
            return r.json()
        except Exception as e:
            print(f"[ERROR] Retrain trigger failed: {e}")
            return None
    
    def print_evolution_report(self, evolution):
        """Print evolution status"""
        if not evolution:
            return
        
        print(f"\n  📊 EVOLUSI STATUS:")
        print(f"     Total Interactions: {evolution['total_interactions']}")
        print(f"     Satisfaction Rate: {evolution['satisfaction']:.1f}%")
        print(f"     Production Model: {evolution['production_model'] or 'None'}")
        print(f"     Model Files: {evolution['model_count']}")
        print(f"     Registry Entries: {evolution['registry_models']}")
    
    def run_daily_mode(self, days=7, interactions_per_day=20):
        """Run daily simulation for N days"""
        print("="*60)
        print("  DEMO 7 HARI EVOLUSI - SELF-EVOLVING AI")
        print("="*60)
        print("\n  Mode: Daily (Real-time)")
        print(f"  Plan: {days} hari × {interactions_per_day} interaksi = {days * interactions_per_day} total")
        
        # Check API
        if not self.check_api():
            print("\n  [ERROR] API tidak berjalan!")
            print("  Jalankan dulu: python run_self_evolving.py")
            return
        
        print("\n  [OK] API connected!")
        
        # Initial status
        evolution = self.check_evolution()
        self.print_evolution_report(evolution)
        
        all_stats = []
        
        for day in range(1, days + 1):
            # Simulate day
            stats = self.simulate_day(day, interactions_per_day)
            all_stats.append(stats)
            
            print(f"\n  ✅ Hari {day} selesai:")
            print(f"     Interactions: {stats['interactions']}")
            print(f"     Positive: {stats['positive']}, Negative: {stats['negative']}")
            print(f"     Avg Latency: {stats['avg_latency']:.1f}ms")
            
            # Check evolution
            evolution = self.check_evolution()
            self.print_evolution_report(evolution)
            
            # Day summary
            if day < days:
                print(f"\n  [INFO] Simulasi hari {day} selesai. Lanjut ke hari {day+1}...")
                print(f"  (Di dunia nyata, ini adalah besok pagi)")
        
        # Final report
        self.print_final_report(all_stats, evolution)
    
    def run_fast_mode(self, total_interactions=100):
        """Fast mode - complete evolution in minutes"""
        print("="*60)
        print("  FAST MODE - SPEEDUP DEMO")
        print("="*60)
        print("\n  Mode: Fast (1 jam = 1 minggu)")
        print(f"  Target: {total_interactions} interaksi cepat")
        
        if not self.check_api():
            print("\n  [ERROR] API tidak berjalan!")
            return
        
        # Initial status
        evolution_before = self.check_evolution()
        print("\n  📊 STATUS AWAL:")
        self.print_evolution_report(evolution_before)
        
        # Generate all interactions quickly
        print(f"\n  [GENERATE] Membuat {total_interactions} interaksi...")
        
        for i in range(total_interactions):
            query = random.choice(QUERIES)
            session_id = f"fast_demo_{i}"
            
            try:
                r = self.session.post(
                    f"{self.base_url}/chat",
                    json={"query": query, "session_id": session_id},
                    timeout=5
                )
                
                if r.status_code == 200:
                    data = r.json()
                    interaction_id = data['interaction_id']
                    
                    # Feedback
                    feedback = 1 if random.random() < 0.7 else 0
                    self.session.post(
                        f"{self.base_url}/feedback",
                        json={
                            "interaction_id": interaction_id,
                            "feedback": feedback
                        },
                        timeout=3
                    )
                
                if (i + 1) % 20 == 0:
                    print(f"    Progress: {i+1}/{total_interactions}")
                
            except Exception as e:
                continue
        
        print("\n  [OK] Interactions generated!")
        
        # Trigger retrain
        print("\n  [TRIGGER] Memaksa retraining...")
        result = self.trigger_retrain()
        
        if result:
            print(f"  Result: {result.get('status', 'unknown')}")
        
        # Check evolution
        evolution_after = self.check_evolution()
        print("\n  📊 STATUS AKHIR:")
        self.print_evolution_report(evolution_after)
        
        # Compare
        print("\n  📈 PERUBAHAN:")
        delta_interactions = evolution_after['total_interactions'] - evolution_before['total_interactions']
        delta_models = evolution_after['model_count'] - evolution_before['model_count']
        
        print(f"     Interactions: +{delta_interactions}")
        print(f"     Models: +{delta_models}")
        print(f"     Satisfaction: {evolution_after['satisfaction']:.1f}%")
    
    def print_final_report(self, all_stats, evolution):
        """Print final evolution report"""
        print("\n" + "="*60)
        print("  LAPORAN AKHIR - 7 HARI EVOLUSI")
        print("="*60)
        
        total_interactions = sum(s['interactions'] for s in all_stats)
        total_positive = sum(s['positive'] for s in all_stats)
        total_negative = sum(s['negative'] for s in all_stats)
        
        print(f"\n  📊 STATISTIK:")
        print(f"     Total Interactions: {total_interactions}")
        print(f"     Positive Feedback: {total_positive}")
        print(f"     Negative Feedback: {total_negative}")
        print(f"     Satisfaction Rate: {evolution['satisfaction']:.1f}%")
        
        print(f"\n  🤖 MODEL EVOLUSI:")
        print(f"     Total Model Files: {evolution['model_count']}")
        print(f"     Production Model: {evolution['current_production'] or 'None'}")
        
        # Check for new models
        if evolution['model_count'] > 1:
            print(f"\n  ✅ MAGIC HAPPENS!")
            print(f"     Model baru telah dibuat!")
            print(f"     AI telah berkembang dari feedback Anda!")
        else:
            print(f"\n  ⏳ Belum cukup data untuk evolusi")
            print(f"     Butuh 50+ feedback untuk trigger retrain")
        
        print(f"\n  📁 FILES:")
        print(f"     Database: logs/feedback/self_improve.db")
        print(f"     Models: models/*.pkl")
        print(f"     Registry: models/model_registry.json")
        
        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(description="Demo 7 Hari Evolusi")
    parser.add_argument("--mode", choices=["daily", "fast"], default="daily",
                       help="Mode: daily (real-time) atau fast (speedup)")
    parser.add_argument("--days", type=int, default=7,
                       help="Jumlah hari (untuk mode daily)")
    parser.add_argument("--interactions", type=int, default=20,
                       help="Interaksi per hari")
    parser.add_argument("--monitor", action="store_true",
                       help="Monitor status saja")
    
    args = parser.parse_args()
    
    demo = EvolutionDemo()
    
    if args.monitor:
        evolution = demo.check_evolution()
        demo.print_evolution_report(evolution)
    elif args.mode == "daily":
        demo.run_daily_mode(args.days, args.interactions)
    else:  # fast mode
        demo.run_fast_mode(args.interactions * args.days)


if __name__ == "__main__":
    main()
