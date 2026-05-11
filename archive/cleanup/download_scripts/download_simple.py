#!/usr/bin/env python
"""
Download all models - Simple version
"""

import os
import sys
from pathlib import Path
from datetime import datetime

models = [
    ("Qwen/Qwen2.5-3B-Instruct-GGUF", "qwen2.5-3b-instruct-q4_k_m.gguf", "Qwen2.5-3B", 0.8),
    ("SeaLLMs/SeaLLM-7B-v2-GGUF", "seallm-7b-v2-q4_k_m.gguf", "SeaLLM-7B", 1.9),
    ("Ichsan2895/Merak-7B-v4-GGUF", "merak-7b-v4-q4_k_m.gguf", "Merak-7B", 1.9),
    ("bartowski/Llama-3.2-3B-Instruct-GGUF", "Llama-3.2-3B-Instruct-Q4_K_M.gguf", "Llama-3.2-3B", 0.8),
    ("bartowski/gemma-2-2b-it-GGUF", "gemma-2-2b-it-Q4_K_M.gguf", "Gemma-2-2B", 0.6),
    ("microsoft/Phi-3.5-mini-instruct-GGUF", "Phi-3.5-mini-instruct-Q4_K_M.gguf", "Phi-3.5-mini", 0.9),
    ("bartowski/c4ai-command-r-v01-GGUF", "c4ai-command-r-v01-Q4_K_M.gguf", "Command-R", 1.0),
    ("TheBloke/stablelm-2-1_6b-chat-GGUF", "stablelm-2-1_6b-chat.Q4_K_M.gguf", "StableLM-2-1.6B", 0.5),
]

os.makedirs("models/llm", exist_ok=True)

print("="*70)
print("KUWERA AI - DOWNLOAD ALL MODELS")
print("="*70)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total models: {len(models)}")
print(f"Estimated size: ~8.4 GB")
print(f"Estimated time: 2-4 hours")
print("="*70)

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    print("Installing huggingface_hub...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface-hub", "-q"])
    from huggingface_hub import hf_hub_download

success = []
failed = []

for i, (repo, filename, name, size_gb) in enumerate(models, 1):
    print(f"\n{'='*70}")
    print(f"MODEL {i}/{len(models)}: {name} ({size_gb} GB)")
    print(f"{'='*70}")
    print(f"Repository: {repo}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    
    # Check if already exists
    target = Path(f"models/llm/{filename}")
    if target.exists():
        actual_size = target.stat().st_size / (1024**3)
        if actual_size >= size_gb * 0.9:
            print(f"Status: ALREADY EXISTS ({actual_size:.2f} GB)")
            success.append((name, actual_size))
            continue
    
    print("Downloading... (this may take 10-30 minutes)")
    print("Please wait...")
    
    try:
        path = hf_hub_download(
            repo_id=repo,
            filename=filename,
            local_dir="models/llm",
            local_dir_use_symlinks=False,
            resume_download=True
        )
        actual_size = os.path.getsize(path) / (1024**3)
        print(f"Status: SUCCESS ({actual_size:.2f} GB)")
        success.append((name, actual_size))
    except Exception as e:
        print(f"Status: FAILED - {e}")
        failed.append(name)
    
    # Progress
    print(f"\nProgress: {len(success)}/{len(models)} models successful")
    print(f"Downloaded: {sum(s for _, s in success):.2f} GB")

# Summary
print("\n" + "="*70)
print("DOWNLOAD COMPLETE")
print("="*70)
print(f"Successful: {len(success)}/{len(models)}")
print(f"Failed: {len(failed)}")

if success:
    print("\nDownloaded models:")
    for name, size in success:
        print(f"  [OK] {name}: {size:.2f} GB")

if failed:
    print("\nFailed models:")
    for name in failed:
        print(f"  [X] {name}")

print("\nAll models in directory:")
for f in sorted(Path("models/llm").glob("*.gguf")):
    size_gb = f.stat().st_size / (1024**3)
    print(f"  {f.name}: {size_gb:.2f} GB")

print("="*70)
