#!/usr/bin/env python
"""
Smart Model Downloader with Resume Support for KUWERA AI
"""

import json
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download, list_repo_files

# Models to download with their priority
MODELS = [
    {
        'repo': 'bartowski/Qwen2.5-Coder-3B-Instruct-GGUF',
        'file': 'Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf',
        'name': 'Qwen2.5-Coder-3B',
        'size': '2.0 GB',
        'priority': 'HIGH'
    },
    {
        'repo': 'bartowski/Qwen2.5-7B-Instruct-GGUF',
        'file': 'Qwen2.5-7B-Instruct-Q4_K_M.gguf',
        'name': 'Qwen2.5-7B',
        'size': '4.4 GB',
        'priority': 'HIGH'
    },
    {
        'repo': 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF',
        'file': 'Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf',
        'name': 'Llama-3.1-8B',
        'size': '4.9 GB',
        'priority': 'MEDIUM'
    },
    {
        'repo': 'bartowski/Llama-3.2-3B-Instruct-GGUF',
        'file': 'Llama-3.2-3B-Instruct-Q4_K_M.gguf',
        'name': 'Llama-3.2-3B',
        'size': '2.0 GB',
        'priority': 'MEDIUM'
    }
]

def download_model(repo_id, filename, local_dir):
    """Download with progress feedback"""
    print(f"  Repo: {repo_id}")
    print(f"  File: {filename}")
    print(f"  Destination: {local_dir}")
    print()
    
    try:
        # Check if already exists
        target_path = Path(local_dir) / filename
        if target_path.exists():
            size_mb = target_path.stat().st_size / (1024*1024)
            print(f"  [INFO] File already exists ({size_mb:.1f} MB)")
            print(f"  [INFO] Skipping download")
            return True
        
        # Download
        print(f"  [DOWNLOADING] Starting download...")
        print(f"  (This may take several minutes for large files)")
        
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        
        print(f"  [OK] Downloaded to: {downloaded_path}")
        return True
        
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

def main():
    models_dir = Path("models/llm")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("KUWERA AI - SMART MODEL DOWNLOADER")
    print("="*70)
    print()
    print("Target Directory:", models_dir.absolute())
    print()
    
    # Check for command line argument
    if len(sys.argv) > 1:
        model_idx = int(sys.argv[1]) - 1
        if 0 <= model_idx < len(MODELS):
            models_to_download = [MODELS[model_idx]]
            print(f"Downloading model #{model_idx + 1} only")
        else:
            print(f"Invalid model number. Available: 1-{len(MODELS)}")
            return
    else:
        models_to_download = MODELS
        print(f"Downloading all {len(MODELS)} models")
    
    print()
    print("="*70)
    
    success_count = 0
    failed_models = []
    
    for i, model in enumerate(models_to_download, 1):
        print()
        print(f"[{i}/{len(models_to_download)}] {model['name']}")
        print(f"Priority: {model['priority']} | Expected Size: {model['size']}")
        print("-"*70)
        
        success = download_model(
            repo_id=model['repo'],
            filename=model['file'],
            local_dir=str(models_dir)
        )
        
        if success:
            success_count += 1
        else:
            failed_models.append(model['name'])
        
        print()
    
    print("="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    print(f"Successful: {success_count}/{len(models_to_download)}")
    
    if failed_models:
        print(f"Failed: {', '.join(failed_models)}")
        print()
        print("For failed downloads, try manual download:")
        for model in MODELS:
            if model['name'] in failed_models:
                print(f"  huggingface-cli download {model['repo']} {model['file']} --local-dir models/llm")
    
    print("="*70)

if __name__ == "__main__":
    main()
