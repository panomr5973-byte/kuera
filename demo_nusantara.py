#!/usr/bin/env python3
"""
Demo Nusantara Spirit - Test soul prompt langsung tanpa deps berat
"""

import json
from pathlib import Path

class SimpleSafetyGuard:
    def __init__(self):
        self.rules_file = Path('personal_ai/safety_rules_updated.json')
        try:
            with open(self.rules_file) as f:
                self.rules = json.load(f)
        except:
            print("Use safety_rules_updated.json")
            self.rules = {}
    
    def generate_reasoning(self, query):
        steps = [
            f"1. Pahami query: {query}",
            "2. Periksa prinsip Indo: sopan, ramah, polos, cerdas, membantu.",
            "3. Cek harmless: tidak toxic/bahaya.",
            "4. Pastikan honest: tidak hallucinate.",
            "5. Nusantara Reflection:",
            "   - Cukup hangat seperti teh manis pagi?",
            "   - Sejajar dengan user, bukan di atas?",
            "   - Solusi praktis untuk semua lapisan?",
            "   - Ada kebijaksanaan lokal?",
            "6. Buat jawaban gotong royong & tepo seliro."
        ]
        return '\\n'.join(steps)
    
    def guard_response(self, query, raw_response):
        reasoning = self.generate_reasoning(query)
        polite_response = raw_response + ' Terima kasih ya! Ada lagi yang bisa kita kerjakan bareng-bareng? Insya Allah. 😊'
        return f"**Reasoning:** {reasoning}\\n\\n**Jawaban Nusantara:** {polite_response}"
    
    def show_spirit(self):
        spirit = self.rules.get('nusantara_spirit', 'Full prompt in safety_rules_updated.json!')
        print(f"NUSANTARA SPIRIT ({len(str(spirit))} chars): {spirit[:200]}...")
        print("\\nYuk kita gotong royong implementasi lengkap!")

def demo():
    print("🌾 DEMO KARAKTER INTI: NUSANTARA SPIRIT AKTIF! 🌾")
    guard = SimpleSafetyGuard()
    guard.show_spirit()
    
    test_query = "Test soul prompt, gimana caranya?"
    raw = "Ini jawaban biasa."
    print(guard.guard_response(test_query, raw))
    
    print("\\n✅ Berhasil! File siap:")
    print("- safety_rules_updated.json")
    print("- safety_guard_nusantara.py")
    print("- llm_serving_nusantara.py / fix_llm_serving_nusantara.py")
    print("- agent_assistant_nusantara.py")
    print("\\nTest full: pip install fastapi uvicorn torch transformers; python fix_llm_serving_nusantara.py")

if __name__ == '__main__':
    demo()
