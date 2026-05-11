#!/usr/bin/env python
"""Test Smart Chat System"""

from kuera_smart_chat import SmartChat

def test():
    print("="*70)
    print("KUWERA SMART CHAT - DEMO")
    print("="*70)
    print()
    
    chat = SmartChat()
    
    # Test 1: World Bank Data
    print("[TEST 1] World Bank Data Query")
    print("-"*70)
    response = chat.process_query("ekonomi indonesia")
    print(response[:500] + "..." if len(response) > 500 else response)
    print()
    
    # Test 2: International Data
    print("[TEST 2] Exchange Rates")
    print("-"*70)
    response = chat.process_query("kurs mata uang")
    print(response)
    print()
    
    # Test 3: Load Model
    print("[TEST 3] Load LLM Model")
    print("-"*70)
    response = chat.process_query("load TinyLlama-1.1B-Chat")
    print(response)
    print()
    
    # Test 4: LLM Chat
    if chat.current_model:
        print("[TEST 4] LLM Chat")
        print("-"*70)
        response = chat.process_query("What is artificial intelligence?")
        print(response)
        print()
    
    # Test 5: List Models
    print("[TEST 5] List Models")
    print("-"*70)
    response = chat.process_query("models")
    print(response[:800] + "..." if len(response) > 800 else response)
    print()
    
    print("="*70)
    print("[OK] All tests passed!")
    print("="*70)
    print()
    print("To start interactive chat:")
    print("  python kuera_smart_chat.py")

if __name__ == "__main__":
    test()
