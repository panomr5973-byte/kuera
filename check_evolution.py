#!/usr/bin/env python
"""
Check Evolution - Cek apakah AI sudah berevolusi
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

def check_evolution():
    print("="*70)
    print("  EVOLUTION CHECK - Self-Evolving AI")
    print("="*70)
    print(f"  Time: {datetime.now()}")
    print("="*70)
    
    evolution_score = 0
    max_score = 5
    
    # 1. Check Database
    print("\n[1/5] DATABASE CHECK")
    db_path = Path("logs/feedback/self_improve.db")
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT COUNT(*) FROM interactions")
            total = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM interactions WHERE user_feedback=1")
            positive = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM interactions WHERE user_feedback=0")
            negative = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"  [OK] Total Interactions: {total}")
            print(f"  [OK] Positive Feedback: {positive}")
            print(f"  [OK] Negative Feedback: {negative}")
            
            if total >= 50:
                print(f"  [BONUS] Threshold 50+ reached! Ready for retrain.")
                evolution_score += 1
            elif total >= 10:
                print(f"  [GOOD] Getting there ({total}/50)")
                evolution_score += 0.5
            else:
                print(f"  [NEED MORE] Only {total} interactions")
                
        except Exception as e:
            print(f"  [ERROR] {e}")
    else:
        print(f"  [MISSING] Database not found")
    
    # 2. Check Models
    print("\n[2/5] MODELS CHECK")
    models_dir = Path("models")
    if models_dir.exists():
        pkl_files = list(models_dir.glob("*.pkl"))
        print(f"  [OK] Model files: {len(pkl_files)}")
        for f in pkl_files:
            print(f"    - {f.name}")
        
        if len(pkl_files) >= 2:
            print(f"  [BONUS] Multiple models = Evolution happened!")
            evolution_score += 1
        elif len(pkl_files) == 1:
            print(f"  [OK] Base model loaded")
            evolution_score += 0.5
    else:
        print(f"  [MISSING] Models directory not found")
    
    # 3. Check Registry
    print("\n[3/5] REGISTRY CHECK")
    registry_path = models_dir / "model_registry.json"
    if registry_path.exists():
        try:
            with open(registry_path) as f:
                registry = json.load(f)
            
            models = registry.get('models', [])
            current_prod = registry.get('current_production')
            
            print(f"  [OK] Registry entries: {len(models)}")
            print(f"  [OK] Production model: {current_prod or 'None'}")
            
            if len(models) >= 2:
                print(f"  [BONUS] Model history exists!")
                evolution_score += 1
            elif len(models) == 1:
                evolution_score += 0.5
                
            # Show model progression
            if models:
                print(f"\n  Model History:")
                for m in models:
                    mid = m.get('model_id', 'unknown')
                    mtype = m.get('model_type', 'unknown')
                    metrics = m.get('metrics', {})
                    f1 = metrics.get('f1_score', 0)
                    print(f"    - {mid} ({mtype}) F1: {f1:.3f}")
                    
        except Exception as e:
            print(f"  [ERROR] {e}")
    else:
        print(f"  [MISSING] Registry not found")
    
    # 4. Check Scheduler Logs
    print("\n[4/5] SCHEDULER CHECK")
    scheduler_log = Path("logs/feedback/scheduler.log")
    if scheduler_log.exists():
        try:
            with open(scheduler_log) as f:
                content = f.read()
            
            if "[OK] Trained" in content:
                count = content.count("[OK] Trained")
                print(f"  [BONUS] Retraining happened! ({count}x)")
                evolution_score += 1
            else:
                print(f"  [PENDING] No retraining yet")
        except:
            print(f"  [ERROR] Cannot read log")
    else:
        print(f"  [MISSING] No scheduler log")
    
    # 5. Check Baseline Metrics
    print("\n[5/5] PERFORMANCE CHECK")
    if registry_path.exists():
        try:
            with open(registry_path) as f:
                registry = json.load(f)
            
            baseline = registry.get('baseline_metrics', {})
            if baseline:
                print(f"  [OK] Baseline metrics:")
                for k, v in baseline.items():
                    print(f"    {k}: {v:.4f}")
                evolution_score += 0.5
            else:
                print(f"  [PENDING] No baseline yet")
        except:
            pass
    
    # Summary
    print("\n" + "="*70)
    print("  EVOLUTION SUMMARY")
    print("="*70)
    
    percentage = (evolution_score / max_score) * 100
    
    print(f"\n  Evolution Score: {evolution_score}/{max_score} ({percentage:.0f}%)")
    
    if percentage >= 80:
        print(f"\n  [EVOLVED!] AI has evolved significantly!")
        print(f"  Models trained, feedback collected, improvements made.")
    elif percentage >= 50:
        print(f"\n  [EVOLVING] AI is in progress...")
        print(f"  Keep interacting to complete evolution!")
    else:
        print(f"\n  [STARTING] Evolution just began...")
        print(f"  Need more interactions and retraining.")
    
    print("\n" + "="*70)
    print("  NEXT STEPS")
    print("="*70)
    
    if evolution_score < 2:
        print("  1. Generate more interactions:")
        print("     python auto_interact.py -n 50")
        print("  2. Or manual interact:")
        print("     python interact.py")
    elif evolution_score < 4:
        print("  1. Check if retraining triggered")
        print("  2. Or force retrain via API")
    else:
        print("  1. Evolution complete!")
        print("  2. Monitor with: python watch_evolution.py")
        print("  3. View dashboard: streamlit run app/dashboard.py")
    
    print("="*70)

if __name__ == "__main__":
    check_evolution()
