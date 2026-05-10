#!/usr/bin/env python
"""
Integrate all downloaded models into Kuera AI
"""

import json
from pathlib import Path

print("="*70)
print("KUWERA AI - MODEL INTEGRATION")
print("="*70)
print()

# Detect all models
models_dir = Path('models/llm')
models = []

model_mapping = {
    'qwen2.5-1.5b-instruct': {'name': 'Qwen2.5-1.5B-Instruct', 'lang': 'Bahasa Indonesia', 'developer': 'Alibaba Cloud', 'priority': 1},
    'qwen2.5-3b-instruct-q2_k': {'name': 'Qwen2.5-3B-Q2', 'lang': 'Bahasa Indonesia', 'developer': 'Alibaba Cloud', 'priority': 2},
    'qwen2.5-3b-instruct-q4_k_m': {'name': 'Qwen2.5-3B-Q4', 'lang': 'Bahasa Indonesia', 'developer': 'Alibaba Cloud', 'priority': 3},
    'seallm-7b-v2': {'name': 'SeaLLM-7B', 'lang': 'Southeast Asia', 'developer': 'DAMO Academy', 'priority': 4},
    'merak-7b-v4': {'name': 'Merak-7B', 'lang': 'Bahasa Indonesia (Local)', 'developer': 'Indonesian AI Community', 'priority': 5},
    'llama-3.2-3b-instruct': {'name': 'Llama-3.2-3B', 'lang': 'Multilingual', 'developer': 'Meta', 'priority': 6},
    'gemma-2-2b-it': {'name': 'Gemma-2-2B', 'lang': 'Multilingual', 'developer': 'Google', 'priority': 7},
    'tinyllama-1.1b-chat': {'name': 'TinyLlama-1.1B', 'lang': 'English', 'developer': 'TinyLlama Team', 'priority': 8},
}

total_size = 0
print("DETECTED MODELS:")
print("-"*70)

for f in sorted(models_dir.glob('*.gguf')):
    size_gb = f.stat().st_size / (1024**3)
    total_size += size_gb
    
    # Detect model info
    fname = f.name.lower()
    info = {
        'filename': f.name, 
        'size_gb': round(size_gb, 2), 
        'path': str(f),
        'name': f.stem[:30], 
        'language': 'Unknown', 
        'developer': 'Unknown',
        'priority': 99
    }
    
    # Smart detection
    if 'qwen' in fname:
        info['developer'] = 'Alibaba Cloud'
        info['language'] = 'Bahasa Indonesia, Multilingual'
        if '1.5b' in fname or '1_5b' in fname:
            info['name'] = 'Qwen2.5-1.5B-Instruct'
            info['priority'] = 1
        elif '3b' in fname or '3_b' in fname:
            if 'q2' in fname:
                info['name'] = 'Qwen2.5-3B-Q2'
                info['priority'] = 2
            else:
                info['name'] = 'Qwen2.5-3B-Q4'
                info['priority'] = 3
    elif 'seallm' in fname:
        info['developer'] = 'DAMO Academy (Alibaba)'
        info['language'] = 'Southeast Asia (Indonesia, Melayu, Thai, etc)'
        info['name'] = 'SeaLLM-7B'
        info['priority'] = 4
    elif 'merak' in fname:
        info['developer'] = 'Indonesian AI Community'
        info['language'] = 'Bahasa Indonesia (Local/Slang)'
        info['name'] = 'Merak-7B'
        info['priority'] = 5
    elif 'llama' in fname:
        info['developer'] = 'Meta'
        info['language'] = 'Multilingual'
        info['name'] = 'Llama-3.2-3B'
        info['priority'] = 6
    elif 'gemma' in fname:
        info['developer'] = 'Google'
        info['language'] = 'Multilingual'
        info['name'] = 'Gemma-2-2B'
        info['priority'] = 7
    elif 'tinyllama' in fname:
        info['developer'] = 'TinyLlama Team'
        info['language'] = 'English'
        info['name'] = 'TinyLlama-1.1B'
        info['priority'] = 8
    
    for key, data in model_mapping.items():
        if key in fname:
            info.update(data)
            break
    
    models.append(info)
    print(f"  [{len(models)}] {info['name']}")
    print(f"      Size: {size_gb:.2f} GB")
    print(f"      Language: {info['language']}")
    print(f"      Developer: {info['developer']}")
    print()

# Sort by priority
models.sort(key=lambda x: x['priority'])

# Save registry
registry = {
    'models': models,
    'total_models': len(models),
    'total_size_gb': round(total_size, 2),
    'indonesian_models': [m['name'] for m in models if 'Indonesia' in m['language']],
    'multilingual_models': [m['name'] for m in models if 'Multilingual' in m['language'] or 'Southeast' in m['language']],
    'specialized': {
        'indonesian_formal': ['Qwen2.5-1.5B-Instruct', 'Qwen2.5-3B-Q4', 'Qwen2.5-3B-Q2'],
        'indonesian_local': ['Merak-7B'],
        'southeast_asia': ['SeaLLM-7B'],
        'multilingual': ['Llama-3.2-3B', 'Gemma-2-2B'],
        'lightweight': ['TinyLlama-1.1B']
    }
}

with open('models/llm/model_registry_active.json', 'w') as f:
    json.dump(registry, f, indent=2)

print("="*70)
print("SUMMARY")
print("="*70)
print(f"Total Models: {len(models)}")
print(f"Total Size: {total_size:.2f} GB")
print(f"Bahasa Indonesia: {len(registry['indonesian_models'])} models")
print(f"Multilingual: {len(registry['multilingual_models'])} models")
print()
print("Registry saved to: models/llm/model_registry_active.json")
print("="*70)
