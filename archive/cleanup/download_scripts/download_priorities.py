#!/usr/bin/env python
"""
Download Priority Models for KUWERA
Download model-model prioritas untuk perkembangan Kuera
"""

import os
import sys
from pathlib import Path

def install_hf():
    """Install huggingface_hub"""
    print("[INSTALL] Installing huggingface_hub...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface-hub", "-q"])
    print("[OK] Installed")

def download_model(repo_id: str, filename: str, models_dir: str) -> bool:
    """Download single model"""
    try:
        from huggingface_hub import hf_hub_download
        
        print(f"\n  Downloading {filename}...")
        print(f"  Repo: {repo_id}")
        print(f"  This may take 10-20 minutes...")
        
        path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=models_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        
        size_gb = os.path.getsize(path) / (1024**3)
        print(f"  [OK] Downloaded: {size_gb:.2f} GB")
        return True
        
    except Exception as e:
        print(f"  [FAILED] {e}")
        return False

def main():
    print("="*70)
    print("KUWERA PRIORITY MODELS DOWNLOAD")
    print("="*70)
    print()
    
    # Check/install huggingface_hub
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        install_hf()
    
    models_dir = "models/llm"
    os.makedirs(models_dir, exist_ok=True)
    
    # Priority models
    priorities = [
        {
            "name": "Qwen2.5-3B-Instruct",
            "repo": "Qwen/Qwen2.5-3B-Instruct-GGUF",
            "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
            "size": "0.8 GB",
            "priority": 1,
            "reason": "Bahasa Indonesia terbaik, balance size/quality"
        },
        {
            "name": "SeaLLM-7B-v2",
            "repo": "SeaLLMs/SeaLLM-7B-v2-GGUF",
            "filename": "seallm-7b-v2-q4_k_m.gguf",
            "size": "1.9 GB",
            "priority": 2,
            "reason": "Southeast Asia specialist"
        },
        {
            "name": "Llama-3.2-3B-Instruct",
            "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
            "filename": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            "size": "0.8 GB",
            "priority": 3,
            "reason": "Meta latest, multilingual"
        }
    ]
    
    print("PRIORITY MODELS TO DOWNLOAD:")
    print("-"*70)
    for i, m in enumerate(priorities, 1):
        print(f"{i}. {m['name']} ({m['size']})")
        print(f"   Why: {m['reason']}")
        print()
    
    print("-"*70)
    total_size = sum([0.8, 1.9, 0.8])
    print(f"Total size: ~{total_size} GB")
    print(f"Location: {os.path.abspath(models_dir)}")
    print("="*70)
    print()
    
    # Confirm
    confirm = input("Continue download? (yes/no): ").lower()
    if confirm != 'yes':
        print("Download cancelled.")
        return
    
    # Download
    success = []
    failed = []
    
    for i, model in enumerate(priorities, 1):
        print(f"\n[{i}/{len(priorities)}] {model['name']}")
        if download_model(model['repo'], model['filename'], models_dir):
            success.append(model['name'])
        else:
            failed.append(model['name'])
    
    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    print(f"Successful: {len(success)}/{len(priorities)}")
    
    if success:
        print("\nDownloaded:")
        for name in success:
            print(f"  [OK] {name}")
    
    if failed:
        print(f"\nFailed:")
        for name in failed:
            print(f"  [X] {name}")
    
    # Check all models
    print("\n" + "-"*70)
    print("ALL DOWNLOADED MODELS:")
    models_path = Path(models_dir)
    for f in sorted(models_path.glob("*.gguf")):
        size_gb = f.stat().st_size / (1024**3)
        print(f"  {f.name} ({size_gb:.2f} GB)")
    
    print("="*70)

if __name__ == "__main__":
    main()
