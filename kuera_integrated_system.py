#!/usr/bin/env python
"""
KUWERA AI - Integrated Multi-Model System v2.0
Full integration with 8 AI models
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import pickle
import numpy as np

try:
    from ctransformers import AutoModelForCausalLM
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logging.warning("ctransformers not installed. Run: pip install ctransformers")


@dataclass
class ModelProfile:
    """Profile untuk setiap model"""
    name: str
    filename: str
    size_gb: float
    language: str
    developer: str
    specialties: List[str]
    context_length: int = 4096
    loaded: bool = False
    use_count: int = 0
    avg_response_time: float = 0.0
    user_rating: float = 0.0


class KueraEvolvingAI:
    """
    Sistem AI Kuera yang terus berevolusi
    """
    
    def __init__(self):
        self.models_dir = Path("models/llm")
        self.data_dir = Path("data")
        self.models: Dict[str, ModelProfile] = {}
        self.loaded_models: Dict[str, any] = {}
        self.model_performance: Dict[str, Dict] = {}
        self.interaction_history = []
        
        self._load_registry()
        self._init_evolution_system()
        
    def _load_registry(self):
        """Load model registry"""
        registry_file = self.models_dir / "model_registry_active.json"
        if registry_file.exists():
            with open(registry_file) as f:
                data = json.load(f)
            
            for m in data.get('models', []):
                # Determine specialties
                specialties = []
                if 'Indonesia' in m.get('language', ''):
                    specialties.append('indonesian')
                if 'Southeast' in m.get('language', ''):
                    specialties.append('southeast_asia')
                if 'Local' in m.get('language', ''):
                    specialties.append('local_slang')
                if 'Multilingual' in m.get('language', ''):
                    specialties.append('multilingual')
                if m.get('size_gb', 0) < 1.0:
                    specialties.append('fast')
                
                profile = ModelProfile(
                    name=m['name'],
                    filename=m['filename'],
                    size_gb=m['size_gb'],
                    language=m['language'],
                    developer=m['developer'],
                    specialties=specialties,
                    context_length=8192 if '7B' in m['name'] else 4096
                )
                self.models[m['name']] = profile
            
            print(f"[OK] Loaded {len(self.models)} models")
        else:
            print("[WARNING] Registry not found")
    
    def _init_evolution_system(self):
        """Initialize evolution tracking system"""
        self.evolution_db = self.data_dir / "kuera_evolution.db"
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize SQLite for tracking
        import sqlite3
        conn = sqlite3.connect(self.evolution_db)
        cursor = conn.cursor()
        
        # Model performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                query_type TEXT,
                response_time REAL,
                user_feedback INTEGER,
                timestamp TEXT,
                query_content TEXT,
                response_content TEXT
            )
        ''')
        
        # Evolution metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolution_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                total_interactions INTEGER,
                avg_satisfaction REAL,
                best_model TEXT,
                improvements TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("[OK] Evolution system initialized")
    
    def select_best_model(self, query: str, context: str = "") -> str:
        """
        Smart model selection dengan machine learning sederhana
        """
        query_lower = query.lower()
        
        # Rule-based dengan scoring
        model_scores = {}
        
        for name, profile in self.models.items():
            score = 0
            
            # Bahasa Indonesia queries
            if any(word in query_lower for word in ['indonesia', 'jakarta', 'nusantara', 'budaya', 'adat']):
                if 'indonesian' in profile.specialties:
                    score += 10
                if 'southeast_asia' in profile.specialties:
                    score += 8
            
            # Local slang
            if any(word in query_lower for word in ['gue', 'lu', 'elo', 'sih', 'dong', 'bete', 'kepo']):
                if 'local_slang' in profile.specialties:
                    score += 15  # Highest priority
            
            # Southeast Asia context
            if any(word in query_lower for word in ['malaysia', 'singapura', 'thailand', 'asean', 'melayu']):
                if 'southeast_asia' in profile.specialties:
                    score += 12
            
            # Technical/Coding queries
            if any(word in query_lower for word in ['code', 'programming', 'python', 'coding', 'algorithm']):
                if 'Qwen' in name or 'Llama' in name:
                    score += 7
            
            # Fast response needed
            if len(query) < 50:  # Short query
                if 'fast' in profile.specialties:
                    score += 5
            
            # Historical performance
            if name in self.model_performance:
                perf = self.model_performance[name]
                score += perf.get('avg_rating', 0) * 2
            
            model_scores[name] = score
        
        # Select best
        if model_scores:
            best_model = max(model_scores, key=model_scores.get)
            return best_model
        
        # Fallback: use first available
        return list(self.models.keys())[0] if self.models else None
    
    def load_model(self, model_name: str) -> any:
        """Load model ke memory"""
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]
        
        if not LLM_AVAILABLE:
            raise ImportError("ctransformers not installed")
        
        profile = self.models.get(model_name)
        if not profile:
            raise ValueError(f"Model {model_name} not found")
        
        model_path = self.models_dir / profile.filename
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        print(f"Loading {model_name}...")
        
        # Determine model type
        fname = profile.filename.lower()
        if 'qwen' in fname:
            model_type = "qwen"
        elif 'llama' in fname:
            model_type = "llama"
        else:
            model_type = "llama"
        
        try:
            model = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                model_type=model_type,
                context_length=profile.context_length
            )
            self.loaded_models[model_name] = model
            profile.loaded = True
            print(f"[OK] {model_name} loaded successfully")
            return model
        except Exception as e:
            print(f"[ERROR] Failed to load {model_name}: {e}")
            raise
    
    def generate(self, query: str, model_name: Optional[str] = None, 
                 system_prompt: str = "", max_tokens: int = 500) -> Dict:
        """
        Generate response dengan tracking
        """
        import time
        
        # Select model
        if model_name is None:
            model_name = self.select_best_model(query)
        
        # Load model
        model = self.load_model(model_name)
        profile = self.models[model_name]
        
        # Build prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {query}\n\nAssistant:"
        else:
            full_prompt = f"User: {query}\n\nAssistant:"
        
        # Generate
        start_time = time.time()
        try:
            response = model(full_prompt, max_new_tokens=max_tokens, temperature=0.7)
            response_time = time.time() - start_time
            
            # Update metrics
            profile.use_count += 1
            profile.avg_response_time = (profile.avg_response_time * (profile.use_count - 1) + response_time) / profile.use_count
            
            # Log to evolution DB
            self._log_interaction(model_name, query, response, response_time)
            
            return {
                'response': response,
                'model_used': model_name,
                'response_time': response_time,
                'model_specialties': profile.specialties,
                'success': True
            }
            
        except Exception as e:
            return {
                'response': f"[Error: {e}]",
                'model_used': model_name,
                'success': False
            }
    
    def _log_interaction(self, model_name: str, query: str, response: str, response_time: float):
        """Log interaction untuk evolution tracking"""
        import sqlite3
        
        conn = sqlite3.connect(self.evolution_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_performance 
            (model_name, query_type, response_time, timestamp, query_content, response_content)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            model_name,
            'chat',
            response_time,
            datetime.now().isoformat(),
            query[:500],  # Truncate
            response[:500]
        ))
        
        conn.commit()
        conn.close()
    
    def get_model_stats(self) -> str:
        """Get statistics untuk semua model"""
        lines = []
        lines.append("="*70)
        lines.append("KUWERA AI - MODEL STATISTICS")
        lines.append("="*70)
        lines.append("")
        
        for name, profile in sorted(self.models.items(), key=lambda x: x[1].use_count, reverse=True):
            lines.append(f"{name}")
            lines.append(f"  Size: {profile.size_gb} GB")
            lines.append(f"  Language: {profile.language}")
            lines.append(f"  Specialties: {', '.join(profile.specialties)}")
            lines.append(f"  Usage Count: {profile.use_count}")
            lines.append(f"  Avg Response Time: {profile.avg_response_time:.2f}s")
            lines.append(f"  Loaded: {'Yes' if profile.loaded else 'No'}")
            lines.append("")
        
        lines.append("="*70)
        return "\n".join(lines)
    
    def provide_feedback(self, model_name: str, rating: int, comment: str = ""):
        """User feedback untuk evolution"""
        if model_name in self.models:
            profile = self.models[model_name]
            # Update rating dengan moving average
            profile.user_rating = (profile.user_rating * profile.use_count + rating) / (profile.use_count + 1)
            print(f"[OK] Feedback recorded for {model_name}: {rating}/5")
    
    def evolve(self):
        """
        Evolve system berdasarkan data
        """
        import sqlite3
        
        conn = sqlite3.connect(self.evolution_db)
        cursor = conn.cursor()
        
        # Get performance data
        cursor.execute('''
            SELECT model_name, AVG(response_time), COUNT(*)
            FROM model_performance
            GROUP BY model_name
        ''')
        
        results = cursor.fetchall()
        
        print("="*70)
        print("KUWERA EVOLUTION ANALYSIS")
        print("="*70)
        print()
        
        for model_name, avg_time, count in results:
            print(f"{model_name}:")
            print(f"  Total interactions: {count}")
            print(f"  Avg response time: {avg_time:.2f}s")
            
            # Recommendations
            if avg_time > 5.0:
                print(f"  Recommendation: Consider using smaller model for this query type")
            if count < 10:
                print(f"  Recommendation: Needs more training data")
            print()
        
        conn.close()
        
        # Save evolution state
        evolution_state = {
            'timestamp': datetime.now().isoformat(),
            'models': {name: asdict(profile) for name, profile in self.models.items()},
            'total_interactions': sum(p.use_count for p in self.models.values())
        }
        
        with open(self.data_dir / 'evolution_state.json', 'w') as f:
            json.dump(evolution_state, f, indent=2, default=str)
        
        print("[OK] Evolution analysis complete")
        print("="*70)


class KueraIntegratedChat:
    """
    Chat interface untuk Kuera Integrated System
    """
    
    def __init__(self):
        self.ai = KueraEvolvingAI()
        self.chat_history = []
        self.system_prompt = """Kamu adalah Kuwera, AI asisten cerdas dari Indonesia. 
Kamu memiliki akses ke berbagai model AI dan data ekonomi Indonesia. 
Jawablah dengan ramah, informatif, dan sesuai konteks budaya Indonesia."""
        
    def start(self):
        """Start interactive chat"""
        print("="*70)
        print("KUWERA AI v2.0 - Integrated Multi-Model System")
        print("="*70)
        print(f"Available Models: {len(self.ai.models)}")
        print(f"Bahasa Indonesia Support: {len([m for m in self.ai.models.values() if 'indonesian' in m.specialties])} models")
        print()
        print("Commands:")
        print("  /models    - List all models")
        print("  /stats     - Show model statistics")
        print("  /evolve    - Run evolution analysis")
        print("  /use <name>- Force use specific model")
        print("  /help      - Show help")
        print("  exit       - Exit chat")
        print("-"*70)
        print()
        
        while True:
            try:
                user_input = input("Anda: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'exit':
                    print("\nTerima kasih! Sampai jumpa! 👋")
                    break
                
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                    continue
                
                # Generate response
                print("\nKuwera (thinking...)")
                result = self.ai.generate(user_input, system_prompt=self.system_prompt)
                
                print(f"\n[Model: {result['model_used']}]")
                print(f"[Specialties: {', '.join(result['model_specialties'])}]")
                print(f"[Time: {result['response_time']:.2f}s]")
                print("-"*70)
                print(result['response'])
                print("-"*70)
                print()
                
                # Save to history
                self.chat_history.append({
                    'user': user_input,
                    'assistant': result['response'],
                    'model': result['model_used']
                })
                
            except KeyboardInterrupt:
                print("\n\nTerima kasih! 👋")
                break
            except Exception as e:
                print(f"[ERROR] {e}")
    
    def handle_command(self, cmd: str):
        """Handle special commands"""
        parts = cmd.split()
        command = parts[0].lower()
        
        if command == '/models':
            print("\n" + self.ai.get_model_stats())
        
        elif command == '/stats':
            print("\n" + self.ai.get_model_stats())
        
        elif command == '/evolve':
            self.ai.evolve()
        
        elif command == '/use' and len(parts) > 1:
            model_name = parts[1]
            if model_name in self.ai.models:
                print(f"[OK] Will use {model_name} for next query")
            else:
                print(f"[ERROR] Model {model_name} not found")
        
        elif command == '/help':
            print("""
Commands:
  /models    - List all available models
  /stats     - Show model statistics and performance
  /evolve    - Run evolution analysis and optimization
  /use <name>- Force use specific model (e.g., /use Merak-7B)
  /help      - Show this help
  exit       - Exit chat

Tips:
  - System automatically selects best model for your query
  - For Indonesian slang, use casual language
  - For formal Indonesian, use proper grammar
  - System learns from interactions and improves over time
            """)
        
        else:
            print(f"[ERROR] Unknown command: {command}")


def main():
    """Main entry point"""
    chat = KueraIntegratedChat()
    chat.start()


if __name__ == "__main__":
    main()
