#!/usr/bin/env python
"""
Watch Evolution - Pantau evolusi real-time
Seperti 'tail -f' untuk AI evolution
"""

import time
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import requests

class EvolutionWatcher:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.last_interactions = 0
        self.last_models = 0
        self.start_time = datetime.now()
        
    def get_stats(self):
        """Get current stats"""
        try:
            # API health
            r = requests.get(f"{self.base_url}/health", timeout=5)
            health = r.json()
            
            # Database
            conn = sqlite3.connect("logs/feedback/self_improve.db")
            cursor = conn.execute("SELECT COUNT(*) FROM interactions")
            total_interactions = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM interactions WHERE user_feedback=1")
            positive = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM interactions WHERE user_feedback=0")
            negative = cursor.fetchone()[0]
            conn.close()
            
            # Models
            models = list(Path("models").glob("*.pkl"))
            model_count = len(models)
            
            # Registry
            registry_path = Path("models/model_registry.json")
            registry = {}
            if registry_path.exists():
                with open(registry_path) as f:
                    registry = json.load(f)
            
            return {
                'interactions': total_interactions,
                'positive': positive,
                'negative': negative,
                'satisfaction': health.get('feedback_stats', {}).get('satisfaction_rate', 0),
                'models': model_count,
                'production': registry.get('current_production', 'None'),
                'registry_count': len(registry.get('models', []))
            }
        except Exception as e:
            return None
    
    def watch(self, interval=5):
        """Watch evolution continuously"""
        print("="*70)
        print("  WATCHING EVOLUTION - Real-time Monitor")
        print("="*70)
        print(f"\n  Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Interval: {interval}s")
        print(f"\n  Tekan Ctrl+C untuk berhenti")
        print("\n" + "="*70)
        
        # Print header
        print(f"{'Time':<12} {'Interact':<10} {'Pos':<6} {'Neg':<6} {'Sat%':<8} {'Models':<8} {'Production':<20}")
        print("-"*70)
        
        try:
            while True:
                stats = self.get_stats()
                now = datetime.now().strftime('%H:%M:%S')
                
                if stats:
                    # Check for changes
                    new_interaction = stats['interactions'] > self.last_interactions
                    new_model = stats['models'] > self.last_models
                    
                    # Format line
                    line = f"{now:<12} {stats['interactions']:<10} {stats['positive']:<6} {stats['negative']:<6} "
                    line += f"{stats['satisfaction']:<8.1f} {stats['models']:<8} {str(stats['production'])[:20]:<20}"
                    
                    # Highlight changes
                    if new_model:
                        line += "  [NEW MODEL!]"
                    elif new_interaction:
                        line += "  [+interact]"
                    
                    print(line)
                    
                    # Update tracking
                    self.last_interactions = stats['interactions']
                    self.last_models = stats['models']
                else:
                    print(f"{now:<12} [ERROR: Cannot connect to API/DB]")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n" + "="*70)
            print("  Stopped by user")
            print("="*70)
            
            # Final summary
            final = self.get_stats()
            if final:
                print(f"\n  FINAL STATS:")
                print(f"    Total Interactions: {final['interactions']}")
                print(f"    Satisfaction: {final['satisfaction']:.1f}%")
                print(f"    Models: {final['models']}")
                print(f"    Production: {final['production']}")

if __name__ == "__main__":
    import sys
    
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    watcher = EvolutionWatcher()
    watcher.watch(interval)
