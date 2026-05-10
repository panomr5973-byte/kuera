#!/usr/bin/env python
"""
Check download progress secara real-time
"""

import os
import time
from pathlib import Path
from datetime import datetime

# Expected models
expected_models = {
    'qwen2.5-1.5b-instruct-q4_k_m.gguf': {'size': 1.04, 'name': 'Qwen2.5-1.5B', 'status': 'done'},
    'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf': {'size': 0.62, 'name': 'TinyLlama-1.1B', 'status': 'done'},
    'qwen2.5-3b-instruct-q4_k_m.gguf': {'size': 0.8, 'name': 'Qwen2.5-3B', 'status': 'pending'},
    'seallm-7b-v2-q4_k_m.gguf': {'size': 1.9, 'name': 'SeaLLM-7B', 'status': 'pending'},
    'merak-7b-v4-q4_k_m.gguf': {'size': 1.9, 'name': 'Merak-7B', 'status': 'pending'},
    'Llama-3.2-3B-Instruct-Q4_K_M.gguf': {'size': 0.8, 'name': 'Llama-3.2-3B', 'status': 'pending'},
    'gemma-2-2b-it-Q4_K_M.gguf': {'size': 0.6, 'name': 'Gemma-2-2B', 'status': 'pending'},
    'Phi-3.5-mini-instruct-Q4_K_M.gguf': {'size': 0.9, 'name': 'Phi-3.5-mini', 'status': 'pending'},
    'c4ai-command-r-v01-Q4_K_M.gguf': {'size': 1.0, 'name': 'Command-R', 'status': 'pending'},
    'stablelm-2-1_6b-chat.Q4_K_M.gguf': {'size': 0.5, 'name': 'StableLM-2-1.6B', 'status': 'pending'},
}

def check_progress():
    models_dir = Path('models/llm')
    
    print("="*70)
    print(f"KUWERA DOWNLOAD PROGRESS - {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    print()
    
    total_expected = len(expected_models)
    downloaded = 0
    total_size = 0
    current_size = 0
    
    for filename, info in expected_models.items():
        file_path = models_dir / filename
        
        if file_path.exists():
            actual_size = file_path.stat().st_size / (1024**3)
            total_size += info['size']
            current_size += actual_size
            
            if actual_size >= info['size'] * 0.95:  # Consider done if 95%+
                status = "✅ DONE"
                downloaded += 1
            else:
                status = f"⏳ {actual_size/info['size']*100:.0f}%"
        else:
            status = "❌ NOT STARTED"
        
        bar = "█" * int((current_size/total_size)*30) if total_size > 0 else "░" * 30
        
        print(f"{info['name']:25} | {info['size']:.1f} GB | {status}")
    
    print()
    print("-"*70)
    pct = (downloaded / total_expected) * 100 if total_expected > 0 else 0
    print(f"PROGRESS: {bar} {downloaded}/{total_expected} models ({pct:.0f}%)")
    print(f"SIZE: {current_size:.2f} / {sum(m['size'] for m in expected_models.values()):.2f} GB")
    print("="*70)

if __name__ == "__main__":
    check_progress()
