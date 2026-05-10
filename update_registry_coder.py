#!/usr/bin/env python
import json
from pathlib import Path
from datetime import datetime

# Load registry
with open('models/llm/model_registry_active.json') as f:
    registry = json.load(f)

# Add Qwen2.5-Coder-3B
new_model = {
    'filename': 'Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf',
    'size_gb': 1.80,
    'path': 'models\\llm\\Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf',
    'name': 'Qwen2.5-Coder-3B',
    'language': 'Bahasa Indonesia, Multilingual (Coding Specialist)',
    'developer': 'Alibaba Cloud (Quantized by Bartowski)',
    'priority': 2,
    'lang': 'Bahasa Indonesia',
    'specialties': ['coding', 'indonesian', 'multilingual', 'technical'],
    'source': 'bartowski/recommended-small-models',
    'added_at': datetime.now().isoformat()
}

# Check if already exists
if not any(m['name'] == 'Qwen2.5-Coder-3B' for m in registry['models']):
    registry['models'].append(new_model)
    registry['models'].sort(key=lambda x: x['priority'])
    
    # Update totals
    registry['total_models'] = len(registry['models'])
    registry['total_size_gb'] = round(sum(m['size_gb'] for m in registry['models']), 2)
    
    # Update categories
    registry['coding_models'] = ['Qwen2.5-Coder-3B']
    registry['bartowski_models'] = ['Qwen2.5-Coder-3B']
    
    # Save
    with open('models/llm/model_registry_active.json', 'w') as f:
        json.dump(registry, f, indent=2)
    
    print('[OK] Qwen2.5-Coder-3B added to registry')
else:
    print('[INFO] Qwen2.5-Coder-3B already in registry')

print()
print('Total models:', registry['total_models'])
print('Total size:', registry['total_size_gb'], 'GB')
print('Coding models:', registry.get('coding_models', []))
