#!/usr/bin/env python
"""
Download semua model dengan progress tracking satu per satu
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

def print_header(title):
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70)

def print_progress(current, total, model_name, status=""):
    pct = (current / total) * 100
    bar = "█" * int(pct/2) + "░" * (50 - int(pct/2))
    print(f"\r[{bar}] {pct:.0f}% | {current}/{total} | {model_name} {status}", end="", flush=True)

def download_model(repo_id, filename, model_name, models_dir):
    """Download single model with progress"""
    try:
        from huggingface_hub import hf_hub_download
        
        print(f"\n📥 Downloading: {model_name}")
        print(f"   Repository: {repo_id}")
        print(f"   File: {filename}")
        print(f"   Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   This may take 10-30 minutes depending on file size...")
        print()
        
        path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=models_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        
        size_gb = os.path.getsize(path) / (1024**3)
        print(f"\n   ✅ SUCCESS: {size_gb:.2f} GB")
        print(f"   Location: {path}")
        return True, size_gb
        
    except Exception as e:
        print(f"\n   ❌ FAILED: {e}")
        return False, 0

def main():
    print_header("KUWERA AI - PROGRESSIVE MODEL DOWNLOAD")
    
    models_dir = "models/llm"
    os.makedirs(models_dir, exist_ok=True)
    
    # Models to download (9 remaining)
    models = [
        ("Qwen/Qwen2.5-3B-Instruct-GGUF", "qwen2.5-3b-instruct-q4_k_m.gguf", "Qwen2.5-3B (0.8 GB) - Bahasa Indonesia"),
        ("SeaLLMs/SeaLLM-7B-v2-GGUF", "seallm-7b-v2-q4_k_m.gguf", "SeaLLM-7B (1.9 GB) - Southeast Asia"),
        ("Ichsan2895/Merak-7B-v4-GGUF", "merak-7b-v4-q4_k_m.gguf", "Merak-7B (1.9 GB) - Buatan Indonesia"),
        ("bartowski/Llama-3.2-3B-Instruct-GGUF", "Llama-3.2-3B-Instruct-Q4_K_M.gguf", "Llama-3.2-3B (0.8 GB) - Multilingual"),
        ("bartowski/gemma-2-2b-it-GGUF", "gemma-2-2b-it-Q4_K_M.gguf", "Gemma-2-2B (0.6 GB) - Google"),
        ("microsoft/Phi-3.5-mini-instruct-GGUF", "Phi-3.5-mini-instruct-Q4_K_M.gguf", "Phi-3.5-mini (0.9 GB) - Microsoft"),
        ("bartowski/c4ai-command-r-v01-GGUF", "c4ai-command-r-v01-Q4_K_M.gguf", "Command-R (1.0 GB) - Long Context"),
        ("TheBloke/stablelm-2-1_6b-chat-GGUF", "stablelm-2-1_6b-chat.Q4_K_M.gguf", "StableLM-2-1.6B (0.5 GB) - Balanced"),
    ]
    
    total_models = len(models)
    print(f"\nTotal models to download: {total_models}")
    print(f"Estimated total size: ~8.4 GB")
    print(f"Estimated time: 2-4 hours")
    print("\n" + "-"*70)
    
    success_list = []
    failed_list = []
    total_downloaded = 0
    
    start_time = time.time()
    
    for i, (repo, filename, name) in enumerate(models, 1):
        print(f"\n{'='*70}")
        print(f"MODEL {i}/{total_models}")
        print(f"{'='*70}")
        
        success, size = download_model(repo, filename, name, models_dir)
        
        if success:
            success_list.append((name, size))
            total_downloaded += size
        else:
            failed_list.append(name)
        
        # Progress summary
        elapsed = time.time() - start_time
        print(f"\n📊 PROGRESS UPDATE:")
        print(f"   Completed: {i}/{total_models}")
        print(f"   Successful: {len(success_list)}")
        print(f"   Failed: {len(failed_list)}")
        print(f"   Downloaded: {total_downloaded:.2f} GB")
        print(f"   Elapsed time: {elapsed/60:.1f} minutes")
        
        if i < total_models:
            print(f"\n⏳ Starting next model in 5 seconds...")
            time.sleep(5)
    
    # Final summary
    print_header("DOWNLOAD COMPLETE")
    print(f"\n📈 FINAL STATISTICS:")
    print(f"   Total models attempted: {total_models}")
    print(f"   Successful: {len(success_list)}")
    print(f"   Failed: {len(failed_list)}")
    print(f"   Total downloaded: {total_downloaded:.2f} GB")
    print(f"   Total time: {(time.time() - start_time)/60:.1f} minutes")
    
    if success_list:
        print(f"\n✅ SUCCESSFULLY DOWNLOADED:")
        for name, size in success_list:
            print(f"   ✓ {name}: {size:.2f} GB")
    
    if failed_list:
        print(f"\n❌ FAILED:")
        for name in failed_list:
            print(f"   ✗ {name}")
    
    # Check all models
    print(f"\n📁 ALL MODELS IN DIRECTORY:")
    models_path = Path(models_dir)
    for f in sorted(models_path.glob("*.gguf")):
        size_gb = f.stat().st_size / (1024**3)
        print(f"   {f.name}: {size_gb:.2f} GB")
    
    print_header("DONE")

if __name__ == "__main__":
    main()
