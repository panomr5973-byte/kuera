#!/usr/bin/env python
"""
Download Bartowski models using new 'hf' CLI syntax
"""

import subprocess
import sys

MODELS = [
    {
        'repo': 'bartowski/Qwen2.5-Coder-3B-Instruct-GGUF',
        'file': 'Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf',
        'name': 'Qwen2.5-Coder-3B',
        'size': '2.0 GB'
    },
    {
        'repo': 'bartowski/Qwen2.5-7B-Instruct-GGUF',
        'file': 'Qwen2.5-7B-Instruct-Q4_K_M.gguf',
        'name': 'Qwen2.5-7B',
        'size': '4.4 GB'
    },
    {
        'repo': 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF',
        'file': 'Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf',
        'name': 'Llama-3.1-8B',
        'size': '4.9 GB'
    },
    {
        'repo': 'bartowski/Llama-3.2-3B-Instruct-GGUF',
        'file': 'Llama-3.2-3B-Instruct-Q4_K_M.gguf',
        'name': 'Llama-3.2-3B',
        'size': '2.0 GB'
    }
]

def download_with_hf(model_idx=None):
    """Download using new hf CLI"""
    
    if model_idx is not None:
        models_to_download = [MODELS[model_idx]]
    else:
        models_to_download = MODELS
    
    for model in models_to_download:
        print(f"\n{'='*60}")
        print(f"Downloading: {model['name']}")
        print(f"Size: {model['size']}")
        print(f"{'='*60}\n")
        
        # New hf CLI syntax
        cmd = [
            'hf', 'download',
            model['repo'],
            model['file'],
            '--local-dir', 'models/llm'
        ]
        
        print(f"Command: {' '.join(cmd)}\n")
        
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print(f"\n[OK] {model['name']} downloaded successfully!")
        else:
            print(f"\n[ERROR] Failed to download {model['name']}")
            return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        idx = int(sys.argv[1]) - 1
        download_with_hf(idx)
    else:
        download_with_hf()
