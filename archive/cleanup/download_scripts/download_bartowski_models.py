#!/usr/bin/env python
"""
Download models from Bartowski's Recommended Small Models collection
Integrate with KUWERA AI
"""

import os
import sys
from pathlib import Path
from datetime import datetime

print("="*70)
print("KUWERA AI - DOWNLOAD FROM BARTOWSKI COLLECTION")
print("="*70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Ensure huggingface_hub is installed
try:
    from huggingface_hub import hf_hub_download
except ImportError:
    print("Installing huggingface_hub...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface-hub", "-q"])
    from huggingface_hub import hf_hub_download

models_dir = "models/llm"
os.makedirs(models_dir, exist_ok=True)

# Priority models from Bartowski collection
models_to_download = [
    {
        'repo': 'bartowski/Qwen2.5-Coder-3B-Instruct-GGUF',
        'filename': 'Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf',
        'name': 'Qwen2.5-Coder-3B',
        'desc': 'Coding specialist, Bahasa Indonesia support',
        'est_size': '1.8 GB'
    },
    {
        'repo': 'bartowski/Qwen2.5-7B-Instruct-GGUF',
        'filename': 'Qwen2.5-7B-Instruct-Q4_K_M.gguf',
        'name': 'Qwen2.5-7B-Instruct',
        'desc': 'General purpose, Bahasa Indonesia, 7B params',
        'est_size': '4.5 GB'
    },
    {
        'repo': 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF',
        'filename': 'Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf',
        'name': 'Llama-3.1-8B-Instruct',
        'desc': 'Meta latest, Multilingual, 8B params',
        'est_size': '5.0 GB'
    },
    {
        'repo': 'bartowski/Llama-3.2-3B-Instruct-GGUF',
        'filename': 'Llama-3.2-3B-Instruct-Q4_K_M.gguf',
        'name': 'Llama-3.2-3B-Instruct',
        'desc': 'Lightweight, Multilingual, 3B params',
        'est_size': '1.9 GB'
    }
]

total_models = len(models_to_download)
print(f"Models to download: {total_models}")
print(f"Estimated total size: ~13-14 GB")
print(f"Estimated time: 2-3 hours (depending on internet)")
print("="*70)
print()

success = []
failed = []

for i, model in enumerate(models_to_download, 1):
    print(f"\n[{i}/{total_models}] {model['name']}")
    print(f"  Repository: {model['repo']}")
    print(f"  Description: {model['desc']}")
    print(f"  Estimated size: {model['est_size']}")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")
    
    # Check if already exists
    target = Path(f"{models_dir}/{model['filename']}")
    if target.exists():
        actual_size = target.stat().st_size / (1024**3)
        print(f"  Status: ALREADY EXISTS ({actual_size:.2f} GB)")
        success.append((model['name'], actual_size))
        continue
    
    print(f"  Downloading... (this may take 20-40 minutes)")
    print(f"  Please wait...")
    
    try:
        path = hf_hub_download(
            repo_id=model['repo'],
            filename=model['filename'],
            local_dir=models_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        actual_size = os.path.getsize(path) / (1024**3)
        print(f"  Status: SUCCESS ({actual_size:.2f} GB)")
        success.append((model['name'], actual_size))
    except Exception as e:
        print(f"  Status: FAILED - {str(e)[:100]}")
        failed.append(model['name'])
    
    # Progress
    print(f"\n  Progress: {len(success)}/{total_models} successful")
    if success:
        print(f"  Downloaded: {sum(s for _, s in success):.2f} GB")

# Summary
print("\n" + "="*70)
print("DOWNLOAD SUMMARY")
print("="*70)
print(f"Successful: {len(success)}/{total_models}")
print(f"Failed: {len(failed)}")

if success:
    print("\nDownloaded models:")
    for name, size in success:
        print(f"  [OK] {name}: {size:.2f} GB")

if failed:
    print("\nFailed models:")
    for name in failed:
        print(f"  [X] {name}")

print("\n" + "-"*70)
print("All models in directory:")
for f in sorted(Path(models_dir).glob("*.gguf")):
    size_gb = f.stat().st_size / (1024**3)
    print(f"  {f.name}: {size_gb:.2f} GB")

print("="*70)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)
