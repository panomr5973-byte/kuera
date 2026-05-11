#!/usr/bin/env python
"""Test Production API"""
import requests
import sys

def test_api():
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("TESTING PRODUCTION API")
    print("="*60)
    
    # 1. Health check
    try:
        r = requests.get(f'{base_url}/health', timeout=5)
        print(f"[OK] Health: {r.json()}")
    except Exception as e:
        print(f"[FAIL] Health check: {e}")
        return False
    
    # 2. Get token
    try:
        r = requests.post(f'{base_url}/token', 
                         data={'username': 'demo', 'password': 'demo123'},
                         timeout=5)
        token = r.json()['access_token']
        print(f"[OK] Token obtained: {token[:20]}...")
    except Exception as e:
        print(f"[FAIL] Authentication: {e}")
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 3. List models
    try:
        r = requests.get(f'{base_url}/models', headers=headers, timeout=5)
        models = r.json()
        print(f"[OK] Models: {models}")
    except Exception as e:
        print(f"[FAIL] List models: {e}")
        return False
    
    # 4. Single prediction
    try:
        r = requests.post(f'{base_url}/predict/best_model_logistic_regression',
                         headers=headers,
                         json={'features': [0.5, -0.3, 1.2, 0.8, -0.5, 0.2, -0.1, 0.6, 0.0]},
                         timeout=5)
        print(f"[OK] Prediction: {r.json()}")
    except Exception as e:
        print(f"[FAIL] Prediction: {e}")
        return False
    
    print("="*60)
    print("ALL TESTS PASSED!")
    print("="*60)
    return True

if __name__ == '__main__':
    success = test_api()
    sys.exit(0 if success else 1)
