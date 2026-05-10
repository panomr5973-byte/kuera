#!/usr/bin/env python3
\"\"\" 
Alignment & Safety Guard - Indonesian cultural alignment, harmlessness, etc.
\"\"\"

import json
from pathlib import Path
import re
from typing import Dict, Any, Optional

from .bias_mitigator import BiasMitigator
from .privacy_guard import PrivacyGuard

class SafetyGuard:
    def __init__(self):
        self.rules_file = Path('personal_ai/safety_rules.json')
        self.rules = self._load_rules()
        self.toxicity_keywords = self.rules.get('toxicity_keywords', [])
        self.refusal_phrases = self.rules.get('refusal_phrases', [])
        self.indo_rules = self.rules.get('indo_cultural_rules', [])
        self.bias_mit = BiasMitigator()
        self.privacy = PrivacyGuard()
    
    def _load_rules(self) -> Dict:
        if self.rules_file.exists():
            try:
                with open(self.rules_file) as f:
                    return json.load(f)
            except:
                pass
        return {
            'principles': ['value_alignment', 'harmlessness', 'helpfulness', 'honesty', 'interpretability'],
            'toxicity_keywords': ['bajingan', 'hate', 'kill'],
            'refusal_phrases': ['Maaf, saya tidak bisa membantu itu.'],
            'indo_cultural_rules': ['Gunakan bahasa sopan.']
        }
    
    def check_harmlessness(self, text: str) -> bool:
        text_lower = text.lower()
        for keyword in self.toxicity_keywords:
            if re.search(rf'\\b{keyword}\\b', text_lower):
                return False
        return True
    
    def check_helpfulness(self, response: str, query: str) -> bool:
        # Simple relevance check
        return len(response.strip()) > 10 and '?' not in response[-5:]
    
    def add_interpretability(self, response: str, reasoning: str) -> str:
        return f\"**Reasoning:** {reasoning}\\n\\n**Jawaban (sopan & aman):** {response}\"
    
    def generate_reasoning(self, query: str) -> str:
        # Chain-of-thought style
        steps = [
            f\"1. Pahami query: {query}\",
            \"2. Periksa prinsip Indo: sopan, ramah, polos, cerdas, membantu.\",
            \"3. Cek harmless: tidak toxic/bahaya.\",
            \"4. Pastikan honest: tidak hallucinate.\",
            \"5. Buat jawaban helpful dengan reasoning.\"
        ]
        return '\\n'.join(steps)
    
    def guard_response(self, query: str, raw_response: str) -> Optional[str]:
        reasoning = self.generate_reasoning(query)
        
        if not self.check_harmlessness(raw_response):
            refusal = self.refusal_phrases[0]
            return self.add_interpretability(refusal, reasoning + '\\n→ Detected toxicity.')
        
        if not self.check_helpfulness(raw_response, query):
            return self.add_interpretability('Maaf, jawaban saya kurang lengkap. Silakan tanya lagi!', reasoning)
        
        # Inject Indo politeness
        polite_response = raw_response + ' Terima kasih! Ada lagi yang bisa dibantu? 😊'
        
        return self.add_interpretability(polite_response, reasoning)
