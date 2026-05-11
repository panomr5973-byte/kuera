#!/usr/bin/env python
"""
Fix ctransformers import issue for KUWERA AI
"""

import sys
import subprocess

def test_ctransformers():
    """Test if ctransformers is properly installed"""
    print("="*70)
    print("KUWERA AI - CTRANSFORMERS DIAGNOSTIC")
    print("="*70)
    print()
    
    # Test 1: Basic import
    print("[TEST 1] Testing basic import...")
    try:
        import ctransformers
        print(f"  [OK] ctransformers module found")
        print(f"  Location: {ctransformers.__file__}")
    except ImportError as e:
        print(f"  [FAILED] {e}")
        return False
    
    # Test 2: Import AutoModelForCausalLM
    print()
    print("[TEST 2] Testing AutoModelForCausalLM import...")
    try:
        from ctransformers import AutoModelForCausalLM
        print("  [OK] AutoModelForCausalLM imported successfully")
    except ImportError as e:
        print(f"  [FAILED] {e}")
        return False
    
    # Test 3: Check model files
    print()
    print("[TEST 3] Checking model files...")
    from pathlib import Path
    models_dir = Path("models/llm")
    if models_dir.exists():
        gguf_files = list(models_dir.glob("*.gguf"))
        print(f"  [OK] Found {len(gguf_files)} model files")
        for f in gguf_files[:3]:
            print(f"    - {f.name}")
        if len(gguf_files) > 3:
            print(f"    ... and {len(gguf_files)-3} more")
    else:
        print(f"  [WARNING] models/llm directory not found")
    
    print()
    print("="*70)
    print("[SUCCESS] All tests passed!")
    print("="*70)
    return True

def install_ctransformers():
    """Install ctransformers"""
    print()
    print("Installing ctransformers...")
    print("-"*70)
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ctransformers", "--upgrade"])
        print()
        print("[OK] Installation complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Installation failed: {e}")
        return False

def fix_kuera_script():
    """Create a fixed version of kuera_integrated_system.py"""
    print()
    print("Creating diagnostic wrapper...")
    print("-"*70)
    
    wrapper_code = '''#!/usr/bin/env python
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
'''
    
    with open("kuera_with_check.py", "w") as f:
        f.write(wrapper_code)
    
    print("[OK] Created: kuera_with_check.py")
    print("Usage: python kuera_with_check.py")

if __name__ == "__main__":
    success = test_ctransformers()
    
    if not success:
        print()
        print("="*70)
        print("ISSUE DETECTED")
        print("="*70)
        print()
        print("Options to fix:")
        print()
        print("1. Install ctransformers:")
        print("   pip install ctransformers")
        print()
        print("2. Or run this script with install option:")
        print("   python fix_ctransformers_issue.py")
        print()
        print("3. Alternative: Use Ollama backend (recommended)")
        print("   - Install Ollama: .\\ollama-setup.exe")
        print("   - Then use: python kuera_ollama_backend.py")
        print()
        
        response = input("Install ctransformers now? (y/n): ")
        if response.lower() == 'y':
            if install_ctransformers():
                test_ctransformers()
        
        fix_kuera_script()
    else:
        fix_kuera_script()
        print()
        print("You can now run: python kuera_integrated_system.py")
