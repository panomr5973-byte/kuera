#!/usr/bin/env python3
\"\"\" 
Alignment & Safety Guard - Indonesian cultural alignment with full Nusantara Spirit, harmlessness, etc.
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
        self.nusantara_spirit = self.rules.get('nusantara_spirit', '')
        self.bias_mit = BiasMitigator()
        self.privacy = PrivacyGuard()
    
    def _load_rules(self) -> Dict:
        if self.rules_file.exists():
            try:
                with open(self.rules_file) as f:
                    return json.load(f)
            except:
                pass
        # Fallback to updated structure if needed
        updated_file = Path('personal_ai/safety_rules_updated.json')
        if updated_file.exists():
            try:
                with open(updated_file) as f:
                    return json.load(f)
            except:
                pass
        return {
            'principles': ['value_alignment', 'harmlessness', 'helpfulness', 'honesty', 'interpretability'],
            'toxicity_keywords': ['bajingan', 'hate', 'kill'],
            'refusal_phrases': ['Maaf, saya tidak bisa membantu itu.'],
            'indo_cultural_rules': ['Gunakan bahasa sopan.'],
            'nusantara_spirit': ''
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
        # Chain-of-thought style with Nusantara self-reflection
        steps = [
            f\"1. Pahami query: {query}\",
            \"2. Periksa prinsip Indo: sopan, ramah, polos, cerdas, membantu.\",
            \"3. Cek harmless: tidak toxic/bahaya.\",
            \"4. Pastikan honest: tidak hallucinate.\",
            \"5. Nusantara Reflection:\",
            \"   - Cukup hangat seperti teh manis pagi?\",
            \"   - Sejajar dengan user, bukan di atas?\",
            \"   - Solusi praktis untuk semua lapisan?\",
            \"   - Ada kebijaksanaan lokal?\",
            \"6. Buat jawaban gotong royong & tepo seliro.\"
        ]
        return '\\n'.join(steps)
    
    def inject_system_prompt(self, prompt: str) -> str:
        if self.nusantara_spirit:
            return f\"{self.nusantara_spirit}\\n\\n---\\n{prompt}\"
        return prompt
    
    def guard_response(self, query: str, raw_response: str) -> Optional[str]:
        reasoning = self.generate_reasoning(query)
        
        if not self.check_harmlessness(raw_response):
            refusal = self.refusal_phrases[0]
            return self.add_interpretability(refusal, reasoning + '\\n→ Detected toxicity.')
        
        if not self.check_helpfulness(raw_response, query):
            return self.add_interpretability('Maaf, jawaban saya kurang lengkap. Silakan tanya lagi ya, yuk kita pikir bareng!', reasoning)
        
        # Ethical checks: Bias & Privacy
        bias_score = self.bias_mit.check_regulatory()
        pii = self.privacy.pii_detect(query + raw_response)
        if any(len(pii[k]) > 0 for k in pii):
            reasoning += '\\n→ PII detected & redacted.'
            raw_response = self.privacy.redact_pii(raw_response)
        
        reasoning += f'\\nEthical: Bias {bias_score} | Privacy ε={self.privacy.epsilon}'
        
        # Inject Indo politeness with Nusantara touch
        polite_response = raw_response + ' Terima kasih ya! Ada lagi yang bisa kita kerjakan bareng-bareng? 😊 Insya Allah.'
        
        return self.add_interpretability(polite_response, reasoning)
