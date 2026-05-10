#!/usr/bin/env python
"""
Demo Real Evolution - Menggunakan data dan model REAL
Prediksi dengan data customer churn, fraud, sales, credit scoring
"""

import os
import sys
import json
import time
import random
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

# API Base URL
API_URL = "http://localhost:8000"

class RealEvolutionDemo:
    """Demo evolusi dengan data real"""
    
    def __init__(self):
        self.session = requests.Session()
        self.models = []
        self.datasets = []
        self._load_available_resources()
    
    def _load_available_resources(self):
        """Load available models and datasets from API"""
        try:
            # Get models
            r = self.session.get(f"{API_URL}/models", timeout=5)
            if r.status_code == 200:
                self.models = r.json().get('models', [])
            
            # Get datasets
            r = self.session.get(f"{API_URL}/datasets", timeout=5)
            if r.status_code == 200:
                self.datasets = r.json().get('datasets', [])
                
        except Exception as e:
            print(f"[ERROR] Cannot connect to API: {e}")
    
    def print_banner(self):
        print("\n" + "="*70)
        print("  DEMO REAL EVOLUTION - Self-Evolving AI dengan Data Nyata")
        print("="*70)
        print("\n  Menggunakan:")
        print("    - Dataset: Customer Churn, Fraud Detection, Sales, Credit Scoring")
        print("    - Model: Logistic Regression, Random Forest, XGBoost, LightGBM")
        print("    - Prediksi: REAL dengan confidence dan feature importance")
        print("="*70)
    
    def print_resources(self):
        print("\n  📊 RESOURCES:")
        print(f"    Models: {len(self.models)}")
        for m in self.models[:3]:  # Show first 3
            print(f"      - {m.get('model_id', 'unknown')}")
        
        print(f"\n    Datasets: {len(self.datasets)}")
        for d in self.datasets:
            print(f"      - {d.get('name')}: {d.get('rows')} rows, {d.get('columns')} cols")
    
    def simulate_real_predictions(self, num_predictions=20):
        """
        Simulate real predictions dengan data nyata
        Setiap prediksi menggunakan sample dari dataset real
        """
        print(f"\n  🔄 SIMULASI {num_predictions} PREDIKSI REAL")
        print("-"*70)
        
        if not self.models:
            print("  [ERROR] No models available!")
            return
        
        if not self.datasets:
            print("  [ERROR] No datasets available!")
            return
        
        results = []
        
        for i in range(num_predictions):
            # Pilih random model dan dataset
            model = random.choice(self.models)
            dataset = random.choice(self.datasets)
            
            model_id = model.get('model_id', 'unknown')
            dataset_name = dataset.get('name', 'unknown')
            
            # Get sample input dari dataset
            sample = dataset.get('sample', {})
            
            try:
                # Prediksi
                r = self.session.post(
                    f"{API_URL}/predict",
                    json={
                        "model_id": model_id,
                        "input_data": sample,
                        "dataset": dataset_name,
                        "session_id": f"demo_real_{i}"
                    },
                    timeout=10
                )
                
                if r.status_code == 200:
                    result = r.json()
                    
                    # Generate feedback berdasarkan confidence
                    confidence = result.get('confidence', 0.5)
                    # Higher confidence = more likely correct
                    is_correct = random.random() < (0.4 + confidence * 0.5)
                    feedback = 1 if is_correct else 0
                    
                    # Submit feedback
                    interaction_id = result.get('interaction_id')
                    if interaction_id:
                        self.session.post(
                            f"{API_URL}/feedback",
                            json={
                                "interaction_id": interaction_id,
                                "feedback": feedback,
                                "reason": "Real data demo" if feedback == 0 else None
                            },
                            timeout=5
                        )
                    
                    results.append({
                        'model': model_id,
                        'dataset': dataset_name,
                        'prediction': result.get('prediction'),
                        'confidence': confidence,
                        'feedback': feedback
                    })
                    
                    # Progress
                    if (i + 1) % 5 == 0:
                        print(f"    Progress: {i+1}/{num_predictions} predictions")
                        print(f"      Last: {model_id} on {dataset_name} → {result.get('prediction_label')} (conf: {confidence:.2f})")
                
            except Exception as e:
                print(f"    [ERROR] Prediction {i}: {e}")
                continue
        
        # Summary
        print(f"\n  ✅ SUMMARY:")
        print(f"    Total predictions: {len(results)}")
        if results:
            correct = sum(1 for r in results if r['feedback'] == 1)
            avg_conf = sum(r['confidence'] for r in results) / len(results)
            print(f"    Correct predictions: {correct}")
            print(f"    Incorrect predictions: {len(results) - correct}")
            print(f"    Average confidence: {avg_conf:.2f}")
        
        return results
    
    def compare_models_performance(self):
        """Compare model performance berdasarkan feedback"""
        print("\n  📊 MODEL PERFORMANCE COMPARISON")
        print("-"*70)
        
        if len(self.models) < 2:
            print("  [INFO] Need at least 2 models to compare")
            return
        
        model1 = self.models[0]
        model2 = self.models[1]
        
        model_id1 = model1.get('model_id')
        model_id2 = model2.get('model_id')
        
        try:
            r = self.session.get(
                f"{API_URL}/compare/{model_id1}/{model_id2}",
                timeout=5
            )
            
            if r.status_code == 200:
                comparison = r.json()
                
                print(f"\n    Comparing:")
                print(f"      Model 1: {model_id1}")
                print(f"        Interactions: {comparison['model_1'].get('interactions', 0)}")
                print(f"        Satisfaction: {comparison['model_1'].get('satisfaction_rate', 0):.1f}%")
                
                print(f"\n      Model 2: {model_id2}")
                print(f"        Interactions: {comparison['model_2'].get('interactions', 0)}")
                print(f"        Satisfaction: {comparison['model_2'].get('satisfaction_rate', 0):.1f}%")
                
                print(f"\n    🏆 Winner: {comparison['comparison']['better_model']}")
                print(f"       Advantage: {comparison['comparison']['satisfaction_diff']:.1f}%")
        
        except Exception as e:
            print(f"    [ERROR] Comparison failed: {e}")
    
    def check_evolution_status(self):
        """Check current evolution status"""
        print("\n  📈 EVOLUTION STATUS")
        print("-"*70)
        
        try:
            r = self.session.get(f"{API_URL}/stats", timeout=5)
            if r.status_code == 200:
                stats = r.json()
                
                # Feedback stats
                feedback = stats.get('feedback', {})
                print(f"    Total feedback: {feedback.get('total_feedback', 0)}")
                print(f"    Positive: {feedback.get('positive', 0)}")
                print(f"    Negative: {feedback.get('negative', 0)}")
                print(f"    Satisfaction: {feedback.get('satisfaction_rate', 0):.1f}%")
                
                # Model count
                print(f"\n    Active models: {len(stats.get('models', []))}")
                print(f"    Datasets: {len(stats.get('datasets', []))}")
        
        except Exception as e:
            print(f"    [ERROR] Cannot get stats: {e}")
    
    def run_full_demo(self):
        """Run full demo"""
        self.print_banner()
        self.print_resources()
        
        # Check API health
        try:
            r = self.session.get(f"{API_URL}/health", timeout=5)
            if r.status_code != 200:
                print("\n  [ERROR] API not running! Start with: python app/real_api.py")
                return
        except:
            print("\n  [ERROR] Cannot connect to API!")
            print("  Start API: python app/real_api.py")
            return
        
        print("\n  [OK] API connected!")
        
        # Phase 1: Initial status
        self.check_evolution_status()
        
        # Phase 2: Generate predictions
        input("\n  Press Enter to start predictions...")
        self.simulate_real_predictions(num_predictions=30)
        
        # Phase 3: Compare models
        input("\n  Press Enter to compare models...")
        self.compare_models_performance()
        
        # Phase 4: Final status
        input("\n  Press Enter to see final status...")
        self.check_evolution_status()
        
        print("\n" + "="*70)
        print("  DEMO COMPLETE!")
        print("="*70)
        print("\n  Next steps:")
        print("    1. Open dashboard: streamlit run app/dashboard.py")
        print("    2. Monitor evolution: python watch_evolution.py")
        print("    3. Trigger retrain: curl -X POST http://localhost:8000/admin/retrain")
        print("="*70)


def main():
    demo = RealEvolutionDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main()
