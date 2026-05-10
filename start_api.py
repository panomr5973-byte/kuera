#!/usr/bin/env python
"""
Launcher for Production API with integrated testing
Run: python start_api.py
"""
import subprocess
import sys
import time
import requests
import threading

def test_api():
    """Test API after server starts"""
    time.sleep(3)  # Wait for server
    try:
        # Health check
        r = requests.get('http://localhost:8000/health', timeout=5)
        print(f"[OK] Health: {r.json()}")
        
        # Get token
        r = requests.post('http://localhost:8000/token', 
                         data={'username': 'demo', 'password': 'demo123'})
        token = r.json()['access_token']
        print(f"[OK] Token obtained: {token[:20]}...")
        
        # List models
        r = requests.get('http://localhost:8000/models',
                        headers={'Authorization': f'Bearer {token}'})
        print(f"[OK] Models: {r.json()}")
        
        # Predict
        r = requests.post('http://localhost:8000/predict/best_model_logistic_regression',
                         headers={'Authorization': f'Bearer {token}'},
                         json={'features': [0.5, -0.3, 1.2, 0.8, -0.5, 0.2, -0.1, 0.6, 0.0]})
        print(f"[OK] Prediction: {r.json()}")
        
        print("\n" + "="*60)
        print("API RUNNING SUCCESSFULLY!")
        print("="*60)
        print("Docs:     http://localhost:8000/docs")
        print("Health:   http://localhost:8000/health")
        print("Models:   http://localhost:8000/models")
        print("\nPress CTRL+C to stop")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

if __name__ == '__main__':
    print("Starting Production API...")
    print("="*60)
    
    # Start test thread
    tester = threading.Thread(target=test_api, daemon=True)
    tester.start()
    
    # Run server
    subprocess.run([sys.executable, 'app/production_api.py'])
