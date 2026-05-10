#!/usr/bin/env python
"""Create model registry for Kuwera"""
import json
from pathlib import Path

models_dir = Path('models/llm')
models_dir.mkdir(parents=True, exist_ok=True)

registry = {
    'available_models': [
        {
            'name': 'Qwen2.5-1.5B-Instruct',
            'repo': 'Qwen/Qwen2.5-1.5B-Instruct-GGUF',
            'filename': 'qwen2.5-1.5b-instruct-q4_k_m.gguf',
            'size_gb': 0.4,
            'priority': 1,
            'description': 'Model multilingual Alibaba (1.5B) - ringan & cepat, support Bahasa Indonesia',
            'tags': ['indonesian', 'multilingual', 'lightweight', 'recommended']
        },
        {
            'name': 'Qwen2.5-3B-Instruct',
            'repo': 'Qwen/Qwen2.5-3B-Instruct-GGUF',
            'filename': 'qwen2.5-3b-instruct-q4_k_m.gguf',
            'size_gb': 0.8,
            'priority': 2,
            'description': 'Model multilingual Alibaba (3B) - support Bahasa Indonesia',
            'tags': ['indonesian', 'multilingual', 'balanced', 'recommended']
        },
        {
            'name': 'Gemma-2-2B-it',
            'repo': 'bartowski/gemma-2-2b-it-GGUF',
            'filename': 'gemma-2-2b-it-Q4_K_M.gguf',
            'size_gb': 0.6,
            'priority': 3,
            'description': 'Google Gemma 2 (2B) - model ringan & powerful',
            'tags': ['multilingual', 'google', 'recommended']
        },
        {
            'name': 'Phi-3.5-mini-instruct',
            'repo': 'microsoft/Phi-3.5-mini-instruct-GGUF',
            'filename': 'Phi-3.5-mini-instruct-Q4_K_M.gguf',
            'size_gb': 0.9,
            'priority': 4,
            'description': 'Microsoft Phi-3.5 Mini - latest version, very capable',
            'tags': ['multilingual', 'microsoft', 'latest']
        },
        {
            'name': 'TinyLlama-1.1B-Chat',
            'repo': 'TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF',
            'filename': 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
            'size_gb': 0.3,
            'priority': 5,
            'description': 'TinyLlama 1.1B - ultra lightweight chat model',
            'tags': ['english', 'ultra-lightweight']
        },
        {
            'name': 'StableLM-2-1.6B-Chat',
            'repo': 'TheBloke/stablelm-2-1_6b-chat-GGUF',
            'filename': 'stablelm-2-1_6b-chat.Q4_K_M.gguf',
            'size_gb': 0.5,
            'priority': 6,
            'description': 'Stability AI StableLM 2 (1.6B) - balanced performance',
            'tags': ['balanced']
        },
        {
            'name': 'Qwen2.5-7B-Instruct',
            'repo': 'Qwen/Qwen2.5-7B-Instruct-GGUF',
            'filename': 'qwen2.5-7b-instruct-q4_k_m.gguf',
            'size_gb': 1.8,
            'priority': 7,
            'description': 'Model multilingual Alibaba (7B) - best quality, support Bahasa Indonesia',
            'tags': ['indonesian', 'multilingual', 'high-quality']
        },
        {
            'name': 'Mistral-7B-Instruct-v0.3',
            'repo': 'MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF',
            'filename': 'mistral-7b-instruct-v0.3.Q3_K_S.gguf',
            'size_gb': 1.9,
            'priority': 8,
            'description': 'Mistral 7B - high quality (Q3 for smaller size)',
            'tags': ['multilingual', 'high-quality']
        }
    ],
    'downloaded': [],
    'failed': []
}

registry_path = models_dir / 'llm_registry.json'
with open(registry_path, 'w') as f:
    json.dump(registry, f, indent=2)

print('='*70)
print('KUWERA LLM MODEL REGISTRY CREATED')
print('='*70)
print(f'Location: {registry_path}')
print(f'Total models: {len(registry["available_models"])}')
print()
print('RECOMMENDED MODELS (Priority Order):')
print('-'*70)
for i, m in enumerate(registry['available_models'], 1):
    tags = ', '.join(m['tags'])
    print(f"{i}. {m['name']}")
    print(f"   Size: {m['size_gb']} GB | Priority: {m['priority']}")
    print(f"   {m['description']}")
    print(f"   Tags: {tags}")
    print()
print('='*70)
total_size = sum(m['size_gb'] for m in registry['available_models'])
print(f'Total size if all downloaded: {total_size:.1f} GB')
print('='*70)
