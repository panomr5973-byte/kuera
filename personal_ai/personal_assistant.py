#!/usr/bin/env python3
"""
Personal AI Assistant - Analyze behavior logs and give proactive suggestions
"""

import json
from pathlib import Path
from datetime import datetime

logs_dir = Path('logs/personal')

def load_behavior_data():
    log_file = logs_dir / 'usage.json'
    if not log_file.exists():
        return None
    
    try:
        with open(log_file) as f:
            return json.load(f)
    except:
        return None

def analyze_behavior():
    data = load_behavior_data()
    if not data:
        return {'message': 'No behavior data yet. Run monitor first.'}
    
    insights = []
    
    # App usage analysis
    apps = data.get('apps', {})
    if apps:
        top_app = max(apps.items(), key=lambda x: len(x[1]))
        insights.append(f'Top app: {top_app[0]} (used {len(top_app[1])} sessions)')
    
    # Patterns
    patterns = data.get('patterns', {})
    hour = patterns.get('active_hour')
    if hour:
        insights.append(f'Peak work hour: {hour}:00')
    
    frequent_files = patterns.get('frequent_files', {})
    if frequent_files:
        top_file = max(frequent_files.items(), key=lambda x: x[1])
        insights.append(f'Frequent file: {top_file[0]} (accessed {top_file[1]}x)')
    
    # Keyboard stats
    kb = data.get('keyboard', {})
    total_keys = kb.get('total_keystrokes', 0)
    if total_keys:
        insights.append(f'Total keystrokes: {total_keys:,}')
        top_kb_app = max(kb.get('apps', {}).items(), key=lambda x: x[1]) if kb.get('apps') else None
        if top_kb_app:
            insights.append(f'Typing most in: {top_kb_app[0]}')
    
    # Proactive suggestions
    suggestions = generate_suggestions(insights)
    
    return {
        'insights': insights,
        'suggestions': suggestions,
        'last_updated': data.get('last_updated'),
        'total_activity': len(data.get('activity', []))
    }

def generate_suggestions(insights):
    suggestions = []
    
    # Rule-based proactivity
    if any('AI-Project' in i for i in insights):
        suggestions.append('💡 You work on AI project - run `python check_evolution.py`?')
    
    if any('code' in i.lower() or 'vscode' in i.lower() for i in insights):
        suggestions.append('💻 VSCode open? Check TODO.md updates.')
    
    hour = datetime.now().hour
    if 9 <= hour <= 11:
        suggestions.append('☕ Coffee break reminder? You\\'re productive now.')
    
    suggestions.append('📊 Full analysis in dashboard.')
    
    return suggestions

if __name__ == '__main__':
    result = analyze_behavior()
    print('🤖 Personal AI Insights:')
    print(json.dumps(result, indent=2, default=str))

