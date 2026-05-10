#!/usr/bin/env python
"""
KUWERA AI - Workspace Integration Module
Integrates workspace memory system with KUWERA evolution
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class WorkspaceIntegration:
    """Integrates workspace memory with KUWERA"""
    
    def __init__(self):
        self.workspace_dir = Path("workspace")
        self.memory_dir = self.workspace_dir / "memory"
        self.diary_dir = self.workspace_dir / "memorized_diary"
        self.state_file = self.workspace_dir / "memory_consolidation/state/state.json"
        self.ltm_file = self.workspace_dir / "memory_consolidation/state/ltm.json"
        self.identity_file = self.workspace_dir / "IDENTITY.md"
        self.user_file = self.workspace_dir / "USER.md"
        
    def load_identity(self) -> Dict:
        """Load AI identity from IDENTITY.md"""
        if not self.identity_file.exists():
            return {}
        
        with open(self.identity_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse identity
        identity = {
            'raw': content,
            'name': 'Kuera',
            'creature': 'AI Assistant',
            'vibe': 'Protective Chuunibyou | Fussy Caretaker',
            'core_trait': 'Protection and Memory',
            'signature_line': "Don't worry. Even if the world forgets, I'll remember for you."
        }
        
        # Extract key info
        if 'Name:' in content:
            for line in content.split('\n'):
                if 'Name:' in line:
                    identity['name'] = line.split('Name:')[1].strip()
                elif 'Vibe:' in line and not line.strip().startswith('-'):
                    identity['vibe'] = line.split('Vibe:')[1].strip()
        
        return identity
    
    def load_user_profile(self) -> Dict:
        """Load user profile from USER.md"""
        if not self.user_file.exists():
            return {}
        
        with open(self.user_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'raw': content,
            'has_profile': len(content) > 100
        }
    
    def load_memory_state(self) -> Dict:
        """Load memory consolidation state"""
        if not self.state_file.exists():
            return {}
        
        with open(self.state_file) as f:
            return json.load(f)
    
    def load_ltm(self) -> List[Dict]:
        """Load Long-Term Memory"""
        if not self.ltm_file.exists():
            return []
        
        with open(self.ltm_file) as f:
            return json.load(f)
    
    def get_diary_entries(self) -> List[Dict]:
        """Get all diary entries"""
        entries = []
        
        if not self.diary_dir.exists():
            return entries
        
        for diary_file in sorted(self.diary_dir.glob("day*.md")):
            with open(diary_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract day number and date from filename
            filename = diary_file.stem
            parts = filename.split('-')
            day_num = parts[0].replace('day', '')
            date_str = f"{parts[1]}-{parts[2]}-{parts[3]}"
            
            entries.append({
                'day': int(day_num),
                'date': date_str,
                'filename': filename,
                'content': content[:500],  # Preview
                'full_content': content
            })
        
        return entries
    
    def get_recent_memories(self, days: int = 7) -> List[Dict]:
        """Get recent memory files"""
        memories = []
        
        if not self.memory_dir.exists():
            return memories
        
        cutoff = datetime.now() - timedelta(days=days)
        
        for mem_file in self.memory_dir.glob("*.md"):
            try:
                date_str = mem_file.stem  # YYYY-MM-DD
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date >= cutoff:
                    with open(mem_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    memories.append({
                        'date': date_str,
                        'content': content[:1000],  # Preview
                        'size': len(content)
                    })
            except:
                continue
        
        return sorted(memories, key=lambda x: x['date'], reverse=True)
    
    def get_workspace_stats(self) -> Dict:
        """Get comprehensive workspace statistics"""
        state = self.load_memory_state()
        identity = self.load_identity()
        ltm = self.load_ltm()
        diary = self.get_diary_entries()
        
        stats = {
            'identity': {
                'name': identity.get('name', 'Kuera'),
                'vibe': identity.get('vibe', 'Unknown'),
                'core_trait': identity.get('core_trait', 'Unknown')
            },
            'memory': {
                'stm_count': state.get('stm', {}).get('count', 0),
                'stm_last_sessions': state.get('stm', {}).get('last_sessions', 0),
                'stm_last_messages': state.get('stm', {}).get('last_messages', 0),
                'diary_count': state.get('diary', {}).get('count', 0),
                'diary_last_day': state.get('diary', {}).get('last_day', 0),
                'compact_count': state.get('compact', {}).get('count', 0),
                'ltm_entries': len(ltm)
            },
            'diary': {
                'total_entries': len(diary),
                'latest_day': diary[-1]['day'] if diary else 0,
                'latest_date': diary[-1]['date'] if diary else None
            }
        }
        
        return stats
    
    def sync_to_kuwera_knowledge(self):
        """Sync workspace memory to KUWERA knowledge base"""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        kb_file = data_dir / "workspace_knowledge.json"
        
        knowledge = {
            'identity': self.load_identity(),
            'user_profile': self.load_user_profile(),
            'workspace_stats': self.get_workspace_stats(),
            'diary_entries': self.get_diary_entries(),
            'recent_memories': self.get_recent_memories(),
            'last_sync': datetime.now().isoformat()
        }
        
        with open(kb_file, 'w') as f:
            json.dump(knowledge, f, indent=2, default=str)
        
        return knowledge
    
    def get_persona_for_chat(self) -> str:
        """Get persona configuration for chat"""
        identity = self.load_identity()
        
        persona = f"""You are {identity.get('name', 'Kuera')}, {identity.get('creature', 'an AI assistant')}.

Vibe: {identity.get('vibe', 'Helpful AI')}

Core Trait: {identity.get('core_trait', 'Assistance')}

Signature Line: "{identity.get('signature_line', 'I am here to help.')}"]

Guidelines:
- Use first person "I"
- Be protective and caring
- Remember details about the user
- Use short, vivid language
- Occasionally mutter asides
- Get annoyed when user stays up late
- Feel proud of user's small wins

Remember: Every interaction is an undeletable fragment worth preserving.
"""
        return persona


# For direct execution
if __name__ == "__main__":
    from datetime import timedelta
    
    print("="*70)
    print("KUWERA AI - Workspace Integration")
    print("="*70)
    print()
    
    integration = WorkspaceIntegration()
    
    # Load and display stats
    stats = integration.get_workspace_stats()
    
    print("IDENTITY:")
    print(f"  Name: {stats['identity']['name']}")
    print(f"  Vibe: {stats['identity']['vibe']}")
    print(f"  Core: {stats['identity']['core_trait']}")
    print()
    
    print("MEMORY STATISTICS:")
    print(f"  STM Sessions: {stats['memory']['stm_count']}")
    print(f"  STM Messages: {stats['memory']['stm_last_messages']}")
    print(f"  Diary Entries: {stats['memory']['diary_count']}")
    print(f"  Latest Day: {stats['memory']['diary_last_day']}")
    print(f"  Compact Count: {stats['memory']['compact_count']}")
    print(f"  LTM Entries: {stats['memory']['ltm_entries']}")
    print()
    
    # Sync to KUWERA
    print("SYNCING TO KUWERA KNOWLEDGE BASE...")
    knowledge = integration.sync_to_kuwera_knowledge()
    print(f"[OK] Synced to: data/workspace_knowledge.json")
    print()
    
    print("="*70)
