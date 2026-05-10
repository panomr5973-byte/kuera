#!/usr/bin/env python
"""
Integrate Bartowski Collection Models into KUWERA AI
"""

import json
from pathlib import Path
from datetime import datetime

print("="*70)
print("KUWERA AI - INTEGRATING BARTOWSKI COLLECTION MODELS")
print("="*70)
print()

models_dir = Path("models/llm")

# Load existing registry
registry_file = models_dir / "model_registry_active.json"
if registry_file.exists():
    with open(registry_file) as f:
        registry = json.load(f)
else:
    registry = {"models": [], "total_models": 0, "total_size_gb": 0}

# Bartowski models configuration
bartowski_models = {
    'qwen2.5-coder-3b': {
        'name': 'Qwen2.5-Coder-3B-Instruct',
        'language': 'Bahasa Indonesia, Multilingual',
        'developer': 'Alibaba Cloud (Quantized by Bartowski)',
        'specialties': ['coding', 'indonesian', 'multilingual', 'technical'],
        'priority': 2,
        'context_length': 32768
    },
    'qwen2.5-7b-instruct': {
        'name': 'Qwen2.5-7B-Instruct',
        'language': 'Bahasa Indonesia, Multilingual',
        'developer': 'Alibaba Cloud (Quantized by Bartowski)',
        'specialties': ['indonesian', 'multilingual', 'general_purpose'],
        'priority': 3,
        'context_length': 32768
    },
    'meta-llama-3.1-8b': {
        'name': 'Meta-Llama-3.1-8B-Instruct',
        'language': 'Multilingual',
        'developer': 'Meta (Quantized by Bartowski)',
        'specialties': ['multilingual', 'general_purpose', 'reasoning'],
        'priority': 4,
        'context_length': 131072
    },
    'llama-3.2-3b-instruct': {
        'name': 'Llama-3.2-3B-Instruct',
        'language': 'Multilingual',
        'developer': 'Meta (Quantized by Bartowski)',
        'specialties': ['multilingual', 'lightweight', 'tool_use'],
        'priority': 5,
        'context_length': 131072
    }
}

# Detect new models
print("DETECTING BARTOWSKI MODELS:")
print("-"*70)

new_models = []
for f in sorted(models_dir.glob("*.gguf")):
    fname_lower = f.name.lower()
    size_gb = f.stat().st_size / (1024**3)
    
    # Check if it's a Bartowski model we want to integrate
    # Handle both lowercase and uppercase filenames
    fname_normalized = fname_lower.replace('-', '').replace('_', '').replace('.', '')
    matched = False
    for key, config in bartowski_models.items():
        key_normalized = key.replace('-', '').replace('_', '').lower()
        if key_normalized in fname_normalized:
            matched = True
            # Check if already in registry
            existing = [m for m in registry['models'] if m['name'] == config['name']]
            if not existing:
                model_entry = {
                    'filename': f.name,
                    'name': config['name'],
                    'size_gb': round(size_gb, 2),
                    'language': config['language'],
                    'developer': config['developer'],
                    'specialties': config['specialties'],
                    'priority': config['priority'],
                    'context_length': config['context_length'],
                    'source': 'bartowski/recommended-small-models',
                    'added_at': datetime.now().isoformat()
                }
                new_models.append(model_entry)
                print(f"  [NEW] {config['name']}")
                print(f"        Size: {size_gb:.2f} GB")
                print(f"        Specialties: {', '.join(config['specialties'])}")
                print()
            else:
                print(f"  [EXISTING] {config['name']}")
            break

# Merge with existing registry
if new_models:
    registry['models'].extend(new_models)
    registry['models'].sort(key=lambda x: x['priority'])
    
    # Update totals
    registry['total_models'] = len(registry['models'])
    registry['total_size_gb'] = round(sum(m['size_gb'] for m in registry['models']), 2)
    
    # Update categories
    registry['bartowski_models'] = [m['name'] for m in registry['models'] if 'bartowski' in m.get('source', '')]
    registry['coding_models'] = [m['name'] for m in registry['models'] if 'coding' in m.get('specialties', [])]
    registry['indonesian_models'] = [m['name'] for m in registry['models'] if 'indonesian' in m.get('specialties', [])]
    registry['multilingual_models'] = [m['name'] for m in registry['models'] if 'multilingual' in m.get('specialties', [])]
    
    # Save updated registry
    with open(registry_file, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"[OK] Added {len(new_models)} new models from Bartowski collection")
else:
    print("[INFO] No new Bartowski models to add")

print()
print("="*70)
print("UPDATED REGISTRY SUMMARY")
print("="*70)
print(f"Total Models: {registry['total_models']}")
print(f"Total Size: {registry['total_size_gb']:.2f} GB")
print(f"Bartowski Models: {len(registry.get('bartowski_models', []))}")
print(f"Coding Models: {len(registry.get('coding_models', []))}")
print(f"Bahasa Indonesia: {len(registry.get('indonesian_models', []))}")
print(f"Multilingual: {len(registry.get('multilingual_models', []))}")
print("="*70)
print()

# Generate model summary table
print("ALL MODELS IN SYSTEM:")
print("-"*70)
for i, m in enumerate(registry['models'], 1):
    source = "Bartowski" if 'bartowski' in m.get('source', '') else "Original"
    print(f"{i}. {m['name']}")
    print(f"   Size: {m['size_gb']} GB | Source: {source}")
    print(f"   Language: {m['language']}")
    print()

print("="*70)
print("[OK] Integration complete!")
print("="*70)
