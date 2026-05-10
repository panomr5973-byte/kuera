#!/usr/bin/env python
"""
Integrate all new Bartowski models into KUWERA AI Registry
"""

import json
from pathlib import Path
from datetime import datetime

print("="*70)
print("KUWERA AI - INTEGRATING ALL NEW MODELS")
print("="*70)
print()

models_dir = Path("models/llm")

# Load existing registry
registry_file = models_dir / "model_registry_active.json"
with open(registry_file) as f:
    registry = json.load(f)

# Define new models to add
new_models = [
    {
        'filename': 'Qwen2.5-7B-Instruct-Q4_K_M.gguf',
        'name': 'Qwen2.5-7B-Instruct',
        'size_gb': 4.36,
        'language': 'Bahasa Indonesia, Multilingual',
        'developer': 'Alibaba Cloud (Quantized by Bartowski)',
        'priority': 3,
        'lang': 'Bahasa Indonesia',
        'specialties': ['indonesian', 'multilingual', 'high_quality'],
        'context_length': 32768,
        'source': 'bartowski/recommended-small-models'
    },
    {
        'filename': 'Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf',
        'name': 'Meta-Llama-3.1-8B-Instruct',
        'size_gb': 4.58,
        'language': 'Multilingual',
        'developer': 'Meta (Quantized by Bartowski)',
        'priority': 4,
        'lang': 'Multilingual',
        'specialties': ['multilingual', 'long_context', 'reasoning'],
        'context_length': 131072,
        'source': 'bartowski/recommended-small-models'
    },
    {
        'filename': 'Llama-3.2-3B-Instruct-Q4_K_M.gguf',
        'name': 'Llama-3.2-3B-Instruct-Q4',
        'size_gb': 1.88,
        'language': 'Multilingual',
        'developer': 'Meta (Quantized by Bartowski)',
        'priority': 6,
        'lang': 'Multilingual',
        'specialties': ['multilingual', 'lightweight', 'tool_use'],
        'context_length': 131072,
        'source': 'bartowski/recommended-small-models'
    }
]

# Track added models
added = []
already_exists = []

for model in new_models:
    # Check if already in registry
    existing = [m for m in registry['models'] if m['name'] == model['name']]
    
    if existing:
        already_exists.append(model['name'])
        continue
    
    # Check if file exists
    model_file = models_dir / model['filename']
    if not model_file.exists():
        print(f"[SKIP] {model['name']} - File not found: {model['filename']}")
        continue
    
    # Add to registry
    model_entry = {
        'filename': model['filename'],
        'name': model['name'],
        'size_gb': model['size_gb'],
        'path': f"models\\llm\\{model['filename']}",
        'language': model['language'],
        'developer': model['developer'],
        'priority': model['priority'],
        'lang': model['lang'],
        'specialties': model['specialties'],
        'context_length': model['context_length'],
        'source': model['source'],
        'added_at': datetime.now().isoformat()
    }
    
    registry['models'].append(model_entry)
    added.append(model['name'])
    print(f"[ADDED] {model['name']} ({model['size_gb']} GB)")

# Sort by priority
registry['models'].sort(key=lambda x: x['priority'])

# Update totals
registry['total_models'] = len(registry['models'])
registry['total_size_gb'] = round(sum(m['size_gb'] for m in registry['models']), 2)

# Update categories
registry['bartowski_models'] = [
    'Qwen2.5-Coder-3B',
    'Qwen2.5-7B-Instruct',
    'Meta-Llama-3.1-8B-Instruct',
    'Llama-3.2-3B-Instruct-Q4'
]

registry['indonesian_models'] = [
    m['name'] for m in registry['models']
    if 'indonesian' in m.get('specialties', []) or 
       'Bahasa Indonesia' in m.get('language', '') or
       m['name'] in ['Qwen2.5-1.5B-Instruct', 'Qwen2.5-3B-Q2', 'Qwen2.5-3B-Q4', 
                     'Qwen2.5-7B-Instruct', 'Qwen2.5-Coder-3B', 'SeaLLM-7B', 'Merak-7B']
]

registry['multilingual_models'] = [
    m['name'] for m in registry['models']
    if 'multilingual' in m.get('specialties', []) or 'Multilingual' in m.get('language', '')
]

registry['coding_models'] = [
    m['name'] for m in registry['models'] if 'coding' in m.get('specialties', [])
]

registry['long_context_models'] = [
    m['name'] for m in registry['models'] 
    if m.get('context_length', 0) > 32000
]

# Save registry
with open(registry_file, 'w') as f:
    json.dump(registry, f, indent=2)

print()
print("="*70)
print("INTEGRATION COMPLETE")
print("="*70)
print()
print(f"New models added: {len(added)}")
for name in added:
    print(f"  + {name}")

if already_exists:
    print(f"\nAlready in registry: {len(already_exists)}")
    for name in already_exists:
        print(f"  = {name}")

print()
print("="*70)
print("UPDATED SYSTEM STATISTICS")
print("="*70)
print(f"Total Models: {registry['total_models']}")
print(f"Total Size: {registry['total_size_gb']:.2f} GB")
print(f"Bartowski Models: {len(registry.get('bartowski_models', []))}")
print(f"Indonesian Models: {len(registry.get('indonesian_models', []))}")
print(f"Multilingual Models: {len(registry.get('multilingual_models', []))}")
print(f"Coding Specialists: {len(registry.get('coding_models', []))}")
print(f"Long Context (>32K): {len(registry.get('long_context_models', []))}")
print("="*70)
print()

# Show all models
print("ALL MODELS IN SYSTEM:")
print("-"*70)
for i, m in enumerate(registry['models'], 1):
    source = "Bartowski" if 'bartowski' in m.get('source', '') else "Original"
    specs = ', '.join(m.get('specialties', []))
    print(f"{i:2}. {m['name']}")
    print(f"    Size: {m['size_gb']:.2f} GB | Source: {source}")
    print(f"    Language: {m['language']}")
    if specs:
        print(f"    Specialties: {specs}")
    print()

print("="*70)
print("[OK] All new models integrated successfully!")
print("="*70)
