#!/usr/bin/env python
"""
Setup Ollama - Download model via Python library
Tanpa perlu install Ollama CLI
"""
import ollama
import sys

def pull_model(model_name="llama3.2:1b"):
    """Pull model menggunakan Ollama Python library"""
    print(f"Downloading model: {model_name}")
    print("This may take a while...")
    
    try:
        # Pull model
        ollama.pull(model_name)
        print(f"[OK] Model {model_name} ready!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to pull model: {e}")
        print("\nNote: Ollama server perlu berjalan.")
        print("Alternatif: Jalankan tanpa Ollama (fallback mode)")
        return False

def test_model(model_name="llama3.2:1b"):
    """Test model dengan simple query"""
    try:
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': 'Halo, apa kabar?'}]
        )
        print(f"\n[OK] Test response: {response['message']['content'][:100]}...")
        return True
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "llama3.2:1b"
    
    print("="*60)
    print("SETUP OLLAMA")
    print("="*60)
    
    if pull_model(model):
        test_model(model)
    else:
        print("\n[SKIP] Ollama tidak tersedia, menggunakan fallback mode")
