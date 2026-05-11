#!/usr/bin/env python
"""Check Kuera Models Status"""

from pathlib import Path
import json

print('='*70)
print('KUWERA AI - MODEL INVENTORY')
print('='*70)
print()

# Check downloaded models
models_dir = Path('models/llm')
downloaded = []
for f in sorted(models_dir.glob('*.gguf')):
    size_gb = f.stat().st_size / (1024**3)
    downloaded.append((f.name, size_gb))

print('MODEL YANG SUDAH DI DOWNLOAD & SIAP PAKAI:')
print('-'*70)
for i, (name, size) in enumerate(downloaded, 1):
    print(f'{i}. {name}')
    print(f'   Size: {size:.2f} GB')
    print()

total_downloaded = sum(s for _, s in downloaded)
print(f'Total Downloaded: {len(downloaded)} models ({total_downloaded:.2f} GB)')
print()

# Check registry
print('='*70)
print('MODEL DALAM REGISTRY (Target):')
print('-'*70)
try:
    with open('models/llm/llm_registry.json') as f:
        registry = json.load(f)
    
    available = registry.get('available_models', [])
    for i, m in enumerate(available, 1):
        name = m.get('name', 'Unknown')
        size_gb = m.get('size_gb', 0)
        desc = m.get('description', '')
        print(f'{i}. {name} ({size_gb} GB)')
        print(f'   {desc}')
        print()
    
    print(f'Total in Registry: {len(available)} models')
    total_target = sum(m.get('size_gb', 0) for m in available)
    print(f'Total Size: {total_target:.2f} GB')
    
    print()
    print('='*70)
    print('SUMMARY:')
    print('='*70)
    print(f'  Model Ready: {len(downloaded)}')
    print(f'  Model Target: {len(available)}')
    if available:
        pct = len(downloaded)/len(available)*100
        print(f'  Progress: {len(downloaded)}/{len(available)} models ({pct:.0f}%)')
    
except Exception as e:
    print(f'Error reading registry: {e}')

print('='*70)
