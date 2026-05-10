#!/usr/bin/env python
"""
Download all models - Auto confirm version
"""

import os
import sys
from pathlib import Path

# Auto confirm
AUTO_CONFIRM = True

models = [
    ("Qwen/Qwen2.5-3B-Instruct-GGUF", "qwen2.5-3b-instruct-q4_k_m.gguf", "Qwen2.5-3B"),
    ("SeaLLMs/SeaLLM-7B-v2-GGUF", "seallm-7b-v2-q4_k_m.gguf", "SeaLLM-7B"),
    ("Ichsan2895/Merak-7B-v4-GGUF", "merak-7b-v4-q4_k_m.gguf", "Merak-7B"),
    ("bartowski/Llama-3.2-3B-Instruct-GGUF", "Llama-3.2-3B-Instruct-Q4_K_M.gguf", "Llama-3.2-3B"),
    ("bartowski/gemma-2-2b-it-GGUF", "gemma-2-2b-it-Q4_K_M.gguf", "Gemma-2-2B"),
    ("microsoft/Phi-3.5-mini-instruct-GGUF", "Phi-3.5-mini-instruct-Q4_K_M.gguf", "Phi-3.5-mini"),
    ("bartowski/c4ai-command-r-v01-GGUF", "c4ai-command-r-v01-Q4_K_M.gguf", "Command-R"),
    ("TheBloke/stablelm-2-1_6b-chat-GGUF", "stablelm-2-1_6b-chat.Q4_K_M.gguf", "StableLM-2-1.6B"),
]

os.makedirs("models/llm", exist_ok=True)

print("="*70)
print("KUWERA - DOWNLOADING ALL MODELS (AUTO)")
print("="*70)
print()

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    print("Installing huggingface_hub...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface-hub", "-q"])
    from huggingface_hub import hf_hub_download

success = []
failed = []

for i, (repo, filename, name) in enumerate(models, 1):
    print(f"\n[{i}/{len(models)}] Downloading {name}...")
    print(f"  Repo: {repo}")
    
    # Check if already exists
    target_path = Path(f"models/llm/{filename}")
    if target_path.exists():
        size_gb = target_path.stat().st_size / (1024**3)
        print(f"  [SKIP] Already exists ({size_gb:.2f} GB)")
        success.append(name)
        continue
    
    try:
        path = hf_hub_download(
            repo_id=repo,
            filename=filename,
            local_dir="models/llm",
            local_dir_use_symlinks=False,
            resume_download=True
        )
        size_gb = os.path.getsize(path) / (1024**3)
        print(f"  [OK] Downloaded: {size_gb:.2f} GB")
        success.append(name)
    except Exception as e:
        print(f"  [FAILED] {e}")
        failed.append(name)

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Success: {len(success)}/{len(models)}")
print(f"Failed: {len(failed)}")

if failed:
    print("\nFailed models:")
    for name in failed:
        print(f"  - {name}")

print("\nDownloaded models:")
for f in sorted(Path("models/llm").glob("*.gguf")):
    size_gb = f.stat().st_size / (1024**3)
    print(f"  {f.name}: {size_gb:.2f} GB")
