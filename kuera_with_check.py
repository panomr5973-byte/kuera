#!/usr/bin/env python
"""
KUWERA AI - Diagnostic Wrapper
Tests environment before starting chat
"""

import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

print("="*70)
print("KUWERA AI - STARTING WITH DIAGNOSTICS")
print("="*70)
print()

# Test imports
print("[1/3] Testing imports...")
try:
    from ctransformers import AutoModelForCausalLM
    print("    [OK] ctransformers available")
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"    [ERROR] ctransformers: {e}")
    print()
    print("[FIX] Run: pip install ctransformers")
    LLM_AVAILABLE = False
    sys.exit(1)

try:
    import numpy
    print("    [OK] numpy available")
except ImportError:
    print("    [WARNING] numpy not found")

print()
print("[2/3] Checking model registry...")
from pathlib import Path
import json

registry_file = Path("models/llm/model_registry_active.json")
if registry_file.exists():
    with open(registry_file) as f:
        registry = json.load(f)
    print(f"    [OK] Registry loaded: {registry.get('total_models', 0)} models")
else:
    print("    [ERROR] Registry not found")
    sys.exit(1)

print()
print("[3/3] All checks passed!")
print("="*70)
print()

# Now run the actual system
print("Starting KUWERA AI Chat Interface...")
print()

exec(open("kuera_integrated_system.py").read())
