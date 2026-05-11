#!/usr/bin/env python
"""
Download Models Simple - Menggunakan huggingface_hub library
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def install_huggingface_hub():
    """Install huggingface_hub library"""
    print("[INSTALL] Installing huggingface_hub...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface-hub", "-q"])
    print("[OK] huggingface_hub installed")

def download_file(repo_id: str, filename: str, local_dir: str) -> bool:
    """Download single file from HuggingFace"""
    try:
        from huggingface_hub import hf_hub_download
        
        print(f"  Downloading {filename}...")
        print(f"  From: {repo_id}")
        print(f"  This may take several minutes depending on file size...")
        
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        
        print(f"  [OK] Downloaded to: {downloaded_path}")
        return True
        
    except Exception as e:
        print(f"  [FAILED] {e}")
        return False

def main():
    print("="*70)
    print("KUWERA MODEL DOWNLOAD (Simple)")
    print("="*70)
    print()
    
    # Install huggingface_hub
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        install_huggingface_hub()
        from huggingface_hub import hf_hub_download
    
    # Load registry
    registry_path = Path("models/llm/llm_registry.json")
    if not registry_path.exists():
        print("[ERROR] Registry not found. Run create_model_registry.py first.")
        return
    
    with open(registry_path) as f:
        registry = json.load(f)
    
    models_dir = Path("models/llm")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Get models to download (top 3 for demo)
    models = sorted(registry['available_models'], key=lambda x: x['priority'])[:3]
    
    print(f"Will download {len(models)} models:")
    total_size = sum(m['size_gb'] for m in models)
    print(f"Total estimated size: {total_size:.1f} GB")
    print(f"Location: {models_dir.absolute()}")
    print()
    
    success = []
    failed = []
    
    for i, model in enumerate(models, 1):
        print(f"[{i}/{len(models)}] {model['name']}")
        print(f"  Size: {model['size_gb']} GB")
        
        if download_file(model['repo'], model['filename'], str(models_dir)):
            success.append(model)
        else:
            failed.append(model)
        print()
    
    # Update registry
    registry['downloaded'] = success
    registry['failed'] = failed
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    # Summary
    print("="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    print(f"Successful: {len(success)}/{len(models)}")
    
    if success:
        print("\nDownloaded:")
        for m in success:
            print(f"  [OK] {m['name']} ({m['size_gb']} GB)")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for m in failed:
            print(f"  [X] {m['name']}")
    
    print("="*70)

if __name__ == "__main__":
    main()
