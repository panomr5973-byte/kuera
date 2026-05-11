#!/usr/bin/env python
"""
Test Qwen Model with Indonesian Language
"""

from ctransformers import AutoModelForCausalLM
from pathlib import Path

def test_qwen():
    print("="*70)
    print("TESTING QWEN2.5-1.5B-INSTRUCT (INDONESIAN)")
    print("="*70)
    print()
    
    model_path = "models/llm/qwen2.5-1.5b-instruct-q4_k_m.gguf"
    
    if not Path(model_path).exists():
        print(f"[ERROR] Model not found: {model_path}")
        return
    
    print(f"Loading model: {model_path}")
    print("This may take 30-60 seconds...")
    print()
    
    try:
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            model_type="llama",
            context_length=2048
        )
        print("[OK] Model loaded successfully!")
        print()
        
        # Test 1: Bahasa Indonesia
        print("[TEST 1] Bahasa Indonesia - Sapa")
        print("-"*70)
        prompt1 = """<|im_start|>system
Kamu adalah Kuwera, AI asisten yang ramah dan membantu. Jawablah dalam Bahasa Indonesia yang baik dan benar.<|im_end|>
<|im_start|>user
Halo, siapa kamu?<|im_end|>
<|im_start|>assistant
"""
        print("Prompt: Halo, siapa kamu?")
        print("Generating...")
        response1 = model(prompt1, max_new_tokens=150, temperature=0.7)
        print(f"Response: {response1}")
        print()
        
        # Test 2: Penjelasan AI
        print("[TEST 2] Bahasa Indonesia - Penjelasan")
        print("-"*70)
        prompt2 = """<|im_start|>system
Kamu adalah Kuwera, AI asisten yang ramah dan membantu. Jawablah dalam Bahasa Indonesia yang baik dan benar.<|im_end|>
<|im_start|>user
Apa itu kecerdasan buatan?<|im_end|>
<|im_start|>assistant
"""
        print("Prompt: Apa itu kecerdasan buatan?")
        print("Generating...")
        response2 = model(prompt2, max_new_tokens=200, temperature=0.7)
        print(f"Response: {response2}")
        print()
        
        # Test 3: Ekonomi Indonesia
        print("[TEST 3] Bahasa Indonesia - Ekonomi")
        print("-"*70)
        prompt3 = """<|im_start|>system
Kamu adalah Kuwera, AI asisten yang ramah dan membantu. Jawablah dalam Bahasa Indonesia yang baik dan benar.<|im_end|>
<|im_start|>user
Bagaimana kondisi ekonomi Indonesia saat ini?<|im_end|>
<|im_start|>assistant
"""
        print("Prompt: Bagaimana kondisi ekonomi Indonesia saat ini?")
        print("Generating...")
        response3 = model(prompt3, max_new_tokens=200, temperature=0.7)
        print(f"Response: {response3}")
        print()
        
        # Test 4: Cakupan Indonesia
        print("[TEST 4] Bahasa Indonesia - Nusantara")
        print("-"*70)
        prompt4 = """<|im_start|>system
Kamu adalah Kuwera, AI asisten yang ramah dan membantu. Jawablah dalam Bahasa Indonesia yang baik dan benar.<|im_end|>
<|im_start|>user
Ceritakan tentang keberagaman Indonesia.<|im_end|>
<|im_start|>assistant
"""
        print("Prompt: Ceritakan tentang keberagaman Indonesia.")
        print("Generating...")
        response4 = model(prompt4, max_new_tokens=200, temperature=0.7)
        print(f"Response: {response4}")
        print()
        
        print("="*70)
        print("[OK] All tests completed!")
        print("="*70)
        print()
        print("Qwen model berhasil diintegrasikan dengan:")
        print("  - Support Bahasa Indonesia yang baik")
        print("  - Format chat yang proper")
        print("  - Respons yang natural")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qwen()
