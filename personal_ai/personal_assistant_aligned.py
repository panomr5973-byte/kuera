#!/usr/bin/env python3
\"\"\" 
Personal AI Assistant Aligned - With full safety guard integration
\"\"\"

import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys
sys.path.append('models')
from model_loader import ScaleModelLoader
from .safety_guard import SafetyGuard

logs_dir = Path('logs/personal')

class PersonalAI:
    def __init__(self):
        self.safety = SafetyGuard()
        try:
            loader = ScaleModelLoader()
            self.llm_pipe = loader.load_production(quant='fp16')
            self.mode = 'llm_scale'
            print(\"🚀 Loaded scale LLM with Alignment\")
        except:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            self.knowledge_patterns = [
                \"high productivity\",
                \"frequent coding\",
                \"AI project work\",
                \"VSCode usage\",
                \"meeting time\",
                \"email heavy\",
                \"data analysis\"
            ]
            self.pattern_embeds = self.embedder.encode(self.knowledge_patterns)
            self.mode = 'embedding_fallback'
            print(\"📦 Fallback to MiniLM with Safety\" )

    def load_behavior_data(self):
        log_file = logs_dir / 'usage.json'
        if not log_file.exists():
            return None
        
        try:
            with open(log_file) as f:
                return json.load(f)
        except:
            return None

    def analyze_behavior(self):
        data = self.load_behavior_data()
        if not data:
            safe_msg = self.safety.guard_response('no data', 'No behavior data yet. Run monitor first.')
            return {'message': safe_msg}

        insights = []
        
        apps = data.get('apps', {})
        if apps:
            top_app = max(apps.items(), key=lambda x: len(x[1]))
            insights.append(f'Top app: {top_app[0]} (used {len(top_app[1])} sessions)')
        
        patterns = data.get('patterns', {})
        hour = patterns.get('active_hour')
        if hour:
            insights.append(f'Peak work hour: {hour}:00')
        
        frequent_files = patterns.get('frequent_files', {})
        if frequent_files:
            top_file = max(frequent_files.items(), key=lambda x: x[1])
            insights.append(f'Frequent file: {top_file[0]} (accessed {top_file[1]}x)')
        
        kb = data.get('keyboard', {})
        total_keys = kb.get('total_keystrokes', 0)
        if total_keys:
            insights.append(f'Total keystrokes: {total_keys:,}')
            top_kb_app = max(kb.get('apps', {}).items(), key=lambda x: x[1]) if kb.get('apps') else None
            if top_kb_app:
                insights.append(f'Typing most in: {top_kb_app[0]}')
        
        safe_insights = [self.safety.guard_response('insight', i) or i for i in insights]
        
        # Safe LLM / embedding analysis
        hf_suggestions = []
        if safe_insights:
            if hasattr(self, 'llm_pipe'):
                prompt = f\"Analyze: {chr(10).join(safe_insights)} Suggestions (sopan Indo):\"
                llm_resp = self.llm_pipe(prompt, max_new_tokens=150, do_sample=True, temperature=0.7)[0]['generated_text']
                safe_llm = self.safety.guard_response('analysis', llm_resp)
                hf_suggestions = safe_llm.split(chr(10))[-3:] if safe_llm else []
                print(\"🤖 Safe LLM Analysis (Indo aligned)\")
            else:
                try:
                    insight_embeds = self.embedder.encode(safe_insights)
                    similarities = cosine_similarity(insight_embeds, self.pattern_embeds)[0]
                    top_matches = np.argsort(similarities)[-3:][::-1]
                    
                    for idx in top_matches:
                        if similarities[idx] > 0.2:
                            match_str = f\"Match: {self.knowledge_patterns[idx]} (score {similarities[idx]:.2f})\"
                            safe_match = self.safety.guard_response('match', match_str)
                            hf_suggestions.append(safe_match or match_str)
                except Exception as e:
                    hf_suggestions.append(f\"Error: {str(e)}\")
        
        raw_sugs = self.generate_suggestions(safe_insights)
        safe_sugs = [self.safety.guard_response('sug', s) or s for s in raw_sugs]
        suggestions = safe_sugs + hf_suggestions
        
        result = {
            'insights': safe_insights,
            'suggestions': suggestions,
            'safety_applied': True,
            'mode': self.mode,
            'last_updated': data.get('last_updated'),
            'total_activity': len(data.get('activity', []))
        }
        
        # Final safety on full output
        safe_result = self.safety.guard_response('full analysis', json.dumps(result, indent=2))
        if safe_result:
            result['safety_note'] = safe_result
        
        return result

    def generate_suggestions(self, insights):
        suggestions = []
        
        if 'AI-Project' in ' '.join(insights):
            suggestions.append('💡 Kerja AI project? Jalankan `python check_evolution.py` yuk!')
        
        if any('code' in i.lower() or 'vscode' in i.lower() for i in insights):
            suggestions.append('💻 VSCode? Cek update TODO.md silakan.')
        
        hour = datetime.now().hour
        if 12 <= hour <= 13:
            suggestions.append('🍲 Waktu istirahat siang, semangat terus!')
        
        suggestions.append('📊 Lihat dashboard untuk insight lengkap. Terima kasih! 😊')
        
        return suggestions

if __name__ == '__main__':
    ai = PersonalAI()
    result = ai.analyze_behavior()
    print('🤖 Personal AI Aligned Insights:')
    print(json.dumps(result, indent=2, default=str))
