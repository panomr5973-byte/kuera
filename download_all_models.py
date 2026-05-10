#!/usr/bin/env python
"""
Download ALL 8 Priority Models for KUWERA
Total: ~8.4 GB
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

def install_hf():
    """Install huggingface_hub"""
    print("[INSTALL] Installing huggingface_hub...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface-hub", "-q"])
    print("[OK] Installed")

def download_with_retry(repo_id: str, filename: str, models_dir: str, max_retries: int = 3) -> bool:
    """Download with retry mechanism"""
    from huggingface_hub import hf_hub_download
    
    for attempt in range(max_retries):
        try:
            print(f"    Attempt {attempt + 1}/{max_retries}...")
            path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=models_dir,
                local_dir_use_symlinks=False,
                resume_download=True
            )
            size_gb = os.path.getsize(path) / (1024**3)
            print(f"    [OK] Downloaded: {size_gb:.2f} GB")
            return True
        except Exception as e:
            print(f"    [FAILED] {e}")
            if attempt < max_retries - 1:
                print(f"    Retrying in 5 seconds...")
                time.sleep(5)
            else:
                return False

def main():
    print("="*70)
    print("KUWERA - DOWNLOAD ALL 8 MODELS")
    print("="*70)
    print()
    
    # Check/install huggingface_hub
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        install_hf()
    
    models_dir = "models/llm"
    os.makedirs(models_dir, exist_ok=True)
    
    # All 8 models
    models = [
        {
            "name": "Qwen2.5-3B-Instruct",
            "repo": "Qwen/Qwen2.5-3B-Instruct-GGUF",
            "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
            "size_gb": 0.8,
            "category": "Bahasa Indonesia",
            "priority": 1
        },
        {
            "name": "SeaLLM-7B-v2",
            "repo": "SeaLLMs/SeaLLM-7B-v2-GGUF",
            "filename": "seallm-7b-v2-q4_k_m.gguf",
            "size_gb": 1.9,
            "category": "Southeast Asia",
            "priority": 2
        },
        {
            "name": "Merak-7B-v4",
            "repo": "Ichsan2895/Merak-7B-v4-GGUF",
            "filename": "merak-7b-v4-q4_k_m.gguf",
            "size_gb": 1.9,
            "category": "Buatan Indonesia",
            "priority": 3
        },
        {
            "name": "Llama-3.2-3B-Instruct",
            "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
            "filename": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            "size_gb": 0.8,
            "category": "Multilingual",
            "priority": 4
        },
        {
            "name": "Gemma-2-2B-it",
            "repo": "bartowski/gemma-2-2b-it-GGUF",
            "filename": "gemma-2-2b-it-Q4_K_M.gguf",
            "size_gb": 0.6,
            "category": "Google Quality",
            "priority": 5
        },
        {
            "name": "Phi-3.5-mini-instruct",
            "repo": "microsoft/Phi-3.5-mini-instruct-GGUF",
            "filename": "Phi-3.5-mini-instruct-Q4_K_M.gguf",
            "size_gb": 0.9,
            "category": "Microsoft",
            "priority": 6
        },
        {
            "name": "Command-R-v01",
            "repo": "bartowski/c4ai-command-r-v01-GGUF",
            "filename": "c4ai-command-r-v01-Q4_K_M.gguf",
            "size_gb": 1.0,
            "category": "Long Context",
            "priority": 7
        },
        {
            "name": "StableLM-2-1.6B-Chat",
            "repo": "TheBloke/stablelm-2-1_6b-chat-GGUF",
            "filename": "stablelm-2-1_6b-chat.Q4_K_M.gguf",
            "size_gb": 0.5,
            "category": "Balanced",
            "priority": 8
        }
    ]
    
    total_size = sum(m['size_gb'] for m in models)
    
    print(f"Will download {len(models)} models")
    print(f"Total estimated size: {total_size:.1f} GB")
    print(f"Location: {os.path.abspath(models_dir)}")
    print()
    print("Models:")
    for i, m in enumerate(models, 1):
        print(f"  {i}. {m['name']} ({m['size_gb']} GB) - {m['category']}")
    print()
    print("="*70)
    print("WARNING: This will take significant time and disk space!")
    print("Estimated download time: 2-4 hours (depending on internet)")
    print("="*70)
    print()
    
    confirm = input("Continue download all 8 models? (yes/no): ").lower()
    if confirm != 'yes':
        print("Download cancelled.")
        return
    
    # Download all
    success = []
    failed = []
    start_time = time.time()
    
    for i, model in enumerate(models, 1):
        print(f"\n[{i}/{len(models)}] {model['name']}")
        print(f"  Category: {model['category']}")
        print(f"  Size: {model['size_gb']} GB")
        print(f"  Repository: {model['repo']}")
        
        if download_with_retry(model['repo'], model['filename'], models_dir):
            success.append(model)
        else:
            failed.append(model)
    
    elapsed = time.time() - start_time
    
    # Update registry
    registry_path = Path(models_dir) / "llm_registry.json"
    if registry_path.exists():
        with open(registry_path) as f:
            registry = json.load(f)
    else:
        registry = {"available_models": [], "downloaded": [], "failed": []}
    
    # Add new models to available
    existing_names = {m['name'] for m in registry['available_models']}
    for model in models:
        if model['name'] not in existing_names:
            registry['available_models'].append(model)
    
    # Update downloaded/failed
    for model in success:
        if model['name'] not in [m['name'] for m in registry['downloaded']]:
            registry['downloaded'].append({
                'name': model['name'],
                'filename': model['filename'],
                'downloaded_at': datetime.now().isoformat()
            })
    
    for model in failed:
        if model['name'] not in [m['name'] for m in registry['failed']]:
            registry['failed'].append({
                'name': model['name'],
                'reason': 'Download failed after retries'
            })
    
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    print(f"Time elapsed: {elapsed/3600:.1f} hours")
    print(f"Successful: {len(success)}/{len(models)}")
    print(f"Failed: {len(failed)}")
    
    if success:
        print("\nDownloaded:")
        for m in success:
            print(f"  [OK] {m['name']} ({m['size_gb']} GB)")
    
    if failed:
        print("\nFailed:")
        for m in failed:
            print(f"  [X] {m['name']}")
        print("\nTo retry failed downloads, run this script again.")
    
    # Check all models
    print("\n" + "-"*70)
    print("ALL DOWNLOADED MODELS:")
    models_path = Path(models_dir)
    gguf_files = list(models_path.glob("*.gguf"))
    total_downloaded = sum(f.stat().st_size for f in gguf_files) / (1024**3)
    
    for f in sorted(gguf_files):
        size_gb = f.stat().st_size / (1024**3)
        print(f"  {f.name}")
        print(f"    Size: {size_gb:.2f} GB")
    
    print(f"\nTotal: {len(gguf_files)} models, {total_downloaded:.2f} GB")
    print("="*70)

if __name__ == "__main__":
    main()
