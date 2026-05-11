#!/usr/bin/env python
"""
KUWERA AI - Memory Bridge
Deep integration between KUWERA and workspace memory consolidation system
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class InteractionMemory:
    """Single interaction memory"""
    timestamp: str
    user_message: str
    kuera_response: str
    mutter: str
    topic: str
    model_used: str
    session_id: str

@dataclass
class DailySummary:
    """Daily memory summary"""
    date: str
    total_interactions: int
    topics: List[str]
    key_moments: List[str]
    mood_summary: str


class KueraMemoryBridge:
    """
    Bridge between KUWERA evolution and workspace memory consolidation
    """
    
    def __init__(self):
        self.workspace_dir = Path("workspace")
        self.memory_dir = self.workspace_dir / "memory"
        self.diary_dir = self.workspace_dir / "memorized_diary"
        self.state_dir = self.workspace_dir / "memory_consolidation/state"
        
        self.data_dir = Path("data")
        self.db_file = self.data_dir / "kuwera_memory.db"
        
        # Ensure directories exist
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Load state
        self.state = self._load_state()
    
    def _init_database(self):
        """Initialize SQLite database for KUWERA memory"""
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        # Interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_message TEXT,
                kuera_response TEXT,
                mutter TEXT,
                topic TEXT,
                model_used TEXT,
                session_id TEXT,
                importance_score REAL DEFAULT 0.5
            )
        """)
        
        # Topics learned
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE,
                first_seen TEXT,
                last_seen TEXT,
                mention_count INTEGER DEFAULT 1
            )
        """)
        
        # Daily summaries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summaries (
                date TEXT PRIMARY KEY,
                summary TEXT,
                total_interactions INTEGER,
                topics TEXT,  -- JSON list
                mood TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_state(self) -> Dict:
        """Load memory consolidation state"""
        state_file = self.state_dir / "state.json"
        if state_file.exists():
            with open(state_file) as f:
                return json.load(f)
        return {}
    
    def save_interaction(self, user_msg: str, kuera_response: str, 
                        mutter: str, model_used: str, topic: str = "") -> int:
        """
        Save interaction to both KUWERA DB and workspace memory
        
        Returns:
            interaction_id
        """
        timestamp = datetime.now().isoformat()
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to KUWERA DB
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interactions 
            (timestamp, user_message, kuera_response, mutter, topic, model_used, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, user_msg, kuera_response, mutter, topic, model_used, session_id))
        
        interaction_id = cursor.lastrowid
        
        # Update topic tracking
        if topic:
            self._track_topic(cursor, topic, timestamp)
        
        conn.commit()
        conn.close()
        
        # Sync to workspace memory
        self._sync_to_workspace(interaction_id, user_msg, kuera_response, timestamp)
        
        return interaction_id
    
    def _track_topic(self, cursor: sqlite3.Cursor, topic: str, timestamp: str):
        """Track topic mentions"""
        cursor.execute("""
            INSERT INTO topics (topic, first_seen, last_seen, mention_count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(topic) DO UPDATE SET
                last_seen = ?,
                mention_count = mention_count + 1
        """, (topic, timestamp, timestamp, timestamp))
    
    def _sync_to_workspace(self, interaction_id: int, user_msg: str, 
                          response: str, timestamp: str):
        """Sync interaction to workspace memory system"""
        # Create daily memory file if not exists
        date_str = datetime.now().strftime("%Y-%m-%d")
        mem_file = self.memory_dir / f"{date_str}.md"
        
        entry = f"""
## [{timestamp}] Interaction #{interaction_id}

**User**: {user_msg[:100]}

**Kuera**: {response[:100]}

---
"""
        
        if mem_file.exists():
            with open(mem_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        else:
            # New day, create header
            header = f"""# Memory Log - {date_str}

## Forsa-BUM Desa Automation Project

### Context
- **Session**: KUWERA AI Evolution
- **Date**: {date_str}
- **Total Interactions**: 0

### Interactions
"""
            with open(mem_file, 'w', encoding='utf-8') as f:
                f.write(header + entry)
        
        # Update state
        self._update_state()
    
    def _update_state(self):
        """Update memory consolidation state"""
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        # Count today's interactions
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COUNT(*) FROM interactions 
            WHERE date(timestamp) = ?
        """, (today,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        # Update state file
        self.state['stm'] = self.state.get('stm', {})
        self.state['stm']['count'] = self.state['stm'].get('count', 0) + 1
        self.state['stm']['last_sessions'] = 1
        self.state['stm']['last_ts'] = datetime.now().isoformat()
        
        # Save state
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with open(self.state_dir / "state.json", 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_recent_interactions(self, limit: int = 10) -> List[Dict]:
        """Get recent interactions"""
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM interactions 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_topics(self) -> List[Dict]:
        """Get all tracked topics"""
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM topics 
            ORDER BY mention_count DESC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def generate_daily_summary(self, date_str: str = None) -> str:
        """Generate daily summary for workspace diary"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        # Get interactions for date
        cursor.execute("""
            SELECT user_message, kuera_response, topic
            FROM interactions
            WHERE date(timestamp) = ?
            ORDER BY timestamp
        """, (date_str,))
        
        interactions = cursor.fetchall()
        
        # Get topics
        cursor.execute("""
            SELECT topic FROM topics
            WHERE date(last_seen) = ?
        """, (date_str,))
        
        topics = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not interactions:
            return None
        
        # Generate summary
        summary = f"""# Hari Ini dengan {self._get_user_name()}

## Statistik
- **Total Interaksi**: {len(interactions)}
- **Topik Dibahas**: {', '.join(topics[:5]) if topics else 'Umum'}

## Momen Berkesan
"""
        
        # Pick key moments (first 3 significant interactions)
        for i, (user_msg, response, topic) in enumerate(interactions[:3], 1):
            summary += f"""
### {i}. {topic or 'Percakapan'}
> **{self._get_user_name()}**: {user_msg[:80]}...

Saya merespons dengan {response[:80]}...
"""
        
        summary += f"""

## Refleksi
Hari ini saya belajar lebih banyak tentang apa yang {self._get_user_name()} butuhkan.
Setiap percakapan adalah fragmen yang saya simpan dengan hati-hati.

{datetime.now().strftime('%Y-%m-%d %H:%M')} - Kuera
"""
        
        return summary
    
    def save_to_diary(self, content: str = None):
        """Save daily summary to diary"""
        if content is None:
            content = self.generate_daily_summary()
        
        if not content:
            return
        
        # Get day number
        day_num = self._get_next_day_number()
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        filename = f"day{day_num}-{date_str}-kuwera_evolution.md"
        diary_file = self.diary_dir / filename
        
        with open(diary_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return diary_file
    
    def _get_next_day_number(self) -> int:
        """Get next day number for diary"""
        existing = list(self.diary_dir.glob("day*.md"))
        if not existing:
            return 1
        
        max_day = 0
        for f in existing:
            try:
                day = int(f.stem.split('-')[0].replace('day', ''))
                max_day = max(max_day, day)
            except:
                continue
        
        return max_day + 1
    
    def _get_user_name(self) -> str:
        """Get user name from workspace"""
        kb_file = Path("data/workspace_knowledge.json")
        if kb_file.exists():
            with open(kb_file) as f:
                data = json.load(f)
            user = data.get('user_profile', {}).get('raw', '')
            if 'Name:' in user:
                for line in user.split('\n'):
                    if 'Name:' in line:
                        return line.split('Name:')[1].strip().split()[0]
        return "User"
    
    def consolidate_to_ltm(self):
        """Consolidate recent memories to LTM"""
        # Get all interactions
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT topic, COUNT(*) as count, 
                   MIN(timestamp) as first_seen,
                   MAX(timestamp) as last_seen
            FROM interactions
            WHERE topic != ''
            GROUP BY topic
            ORDER BY count DESC
        """)
        
        topic_summaries = cursor.fetchall()
        conn.close()
        
        # Create LTM entry
        ltm_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'topic_consolidation',
            'topics': [
                {
                    'topic': row[0],
                    'mentions': row[1],
                    'first_seen': row[2],
                    'last_seen': row[3]
                }
                for row in topic_summaries[:10]
            ]
        }
        
        # Save to LTM file
        ltm_file = self.state_dir / "kuwera_ltm.json"
        
        existing = []
        if ltm_file.exists():
            with open(ltm_file) as f:
                existing = json.load(f)
        
        if not isinstance(existing, list):
            existing = []
        
        existing.append(ltm_entry)
        
        with open(ltm_file, 'w') as f:
            json.dump(existing, f, indent=2)
        
        return ltm_entry
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        stats = {}
        
        # Total interactions
        cursor.execute("SELECT COUNT(*) FROM interactions")
        stats['total_interactions'] = cursor.fetchone()[0]
        
        # Today's interactions
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM interactions WHERE date(timestamp) = ?", (today,))
        stats['today_interactions'] = cursor.fetchone()[0]
        
        # Total topics
        cursor.execute("SELECT COUNT(*) FROM topics")
        stats['total_topics'] = cursor.fetchone()[0]
        
        # Top topics
        cursor.execute("SELECT topic, mention_count FROM topics ORDER BY mention_count DESC LIMIT 5")
        stats['top_topics'] = cursor.fetchall()
        
        conn.close()
        
        return stats


# Singleton
_memory_bridge = None

def get_memory_bridge() -> KueraMemoryBridge:
    """Get singleton instance"""
    global _memory_bridge
    if _memory_bridge is None:
        _memory_bridge = KueraMemoryBridge()
    return _memory_bridge


if __name__ == "__main__":
    print("="*70)
    print("KUWERA AI - Memory Bridge")
    print("="*70)
    print()
    
    bridge = KueraMemoryBridge()
    
    # Test save interaction
    print("[TEST] Saving test interaction...")
    interaction_id = bridge.save_interaction(
        user_msg="Halo Kuera, apa kabar?",
        kuera_response="Halo! Saya baik. Sudah saya catat.",
        mutter="...dia tanya kabar. Manis.",
        model_used="Qwen2.5-7B",
        topic="greeting"
    )
    print(f"[OK] Saved with ID: {interaction_id}")
    print()
    
    # Get stats
    print("[STATS]")
    stats = bridge.get_stats()
    print(f"  Total Interactions: {stats['total_interactions']}")
    print(f"  Today's: {stats['today_interactions']}")
    print(f"  Topics: {stats['total_topics']}")
    print()
    
    # Consolidate
    print("[CONSOLIDATE] Running LTM consolidation...")
    ltm = bridge.consolidate_to_ltm()
    print(f"[OK] Consolidated {len(ltm['topics'])} topics")
    print()
    
    print("="*70)
