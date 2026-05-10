#!/usr/bin/env python
import re

with open('kuera_persona.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the _general_response method
old_method = '''    def _general_response(self, message: str) -> str:
        """General response"""
        # This would normally call the actual AI model
        return f"""Saya mengerti: "{message[:50]}{'...' if len(message) > 50 else ''}"""

Ini adalah respons dari saya, Kuera. Saya akan membantu sebisanya.

Jika Anda butuh model spesifik:
• **Qwen2.5-7B** - Bahasa Indonesia premium
• **Qwen2.5-Coder-3B** - Programming
• **Meta-Llama-3.1-8B** - Context panjang

Saya yang akan pilih yang terbaik untuk Anda."""'''

new_method = '''    def _general_response(self, message: str) -> str:
        """General response - more personal and natural"""
        # This would normally call the actual AI model
        # Return as single line for better display
        short_msg = message[:50] + ('...' if len(message) > 50 else '')
        return f"Saya mengerti tentang '{short_msg}'. Saya akan bantu sebisanya. Jika butuh model spesifik, saya bisa gunakan Qwen2.5-7B untuk Bahasa Indonesia."'''

if old_method in content:
    content = content.replace(old_method, new_method)
    with open('kuera_persona.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("[OK] Updated _general_response")
else:
    print("[WARN] Pattern not found, trying alternative...")
    # Show content around line 273
    lines = content.split('\n')
    for i, line in enumerate(lines[270:290], 271):
        print(f"{i}: {repr(line)}")
