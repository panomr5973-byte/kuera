#!/usr/bin/env python
"""
KUWERA Evolution Engine
Sistem evolusi dan pembelajaran berkelanjutan untuk Kuera AI
"""

import json
import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pickle


class EvolutionEngine:
    """
    Engine untuk evolusi AI berdasarkan interaksi dan feedback
    """
    
    def __init__(self, db_path: str = "data/kuera_evolution.db"):
        self.db_path = Path(db_path)
        self.models_dir = Path("models/llm")
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        self._init_database()
        self.evolution_state = self._load_evolution_state()
        
    def _init_database(self):
        """Initialize evolution database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                model_name TEXT,
                query TEXT,
                response TEXT,
                query_type TEXT,
                response_time REAL,
                user_feedback INTEGER,
                user_rating INTEGER,
                context TEXT
            )
        ''')
        
        # Model performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                date TEXT,
                total_queries INTEGER,
                avg_response_time REAL,
                avg_rating REAL,
                success_rate REAL,
                improvement_score REAL
            )
        ''')
        
        # Evolution history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                generation INTEGER,
                best_model TEXT,
                avg_performance REAL,
                changes_made TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _load_evolution_state(self) -> Dict:
        """Load current evolution state"""
        state_file = self.data_dir / "evolution_state.pkl"
        if state_file.exists():
            with open(state_file, 'rb') as f:
                return pickle.load(f)
        return {
            'generation': 0,
            'total_interactions': 0,
            'model_weights': {},
            'learning_rate': 0.1,
            'last_evolution': None
        }
    
    def _save_evolution_state(self):
        """Save evolution state"""
        state_file = self.data_dir / "evolution_state.pkl"
        with open(state_file, 'wb') as f:
            pickle.dump(self.evolution_state, f)
    
    def record_interaction(self, model_name: str, query: str, response: str,
                          response_time: float, user_rating: int = 0,
                          query_type: str = "general", context: str = ""):
        """Record interaction untuk training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interactions 
            (timestamp, model_name, query, response, query_type, response_time, user_rating, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            model_name,
            query[:1000],  # Truncate
            response[:1000],
            query_type,
            response_time,
            user_rating,
            context
        ))
        
        conn.commit()
        conn.close()
        
        # Update state
        self.evolution_state['total_interactions'] += 1
        
        # Update model weights dengan reinforcement learning sederhana
        if model_name not in self.evolution_state['model_weights']:
            self.evolution_state['model_weights'][model_name] = 1.0
        
        # Adjust weight based on rating
        if user_rating > 0:
            reward = (user_rating - 3) / 2.0  # Normalize to -1 to 1
            self.evolution_state['model_weights'][model_name] += reward * self.evolution_state['learning_rate']
            self.evolution_state['model_weights'][model_name] = max(0.1, min(5.0, self.evolution_state['model_weights'][model_name]))
        
        self._save_evolution_state()
    
    def analyze_performance(self, days: int = 7) -> Dict:
        """Analyze performance dalam periode tertentu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get model performance
        cursor.execute('''
            SELECT 
                model_name,
                COUNT(*) as total_queries,
                AVG(response_time) as avg_time,
                AVG(user_rating) as avg_rating,
                SUM(CASE WHEN user_rating >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as satisfaction_rate
            FROM interactions
            WHERE timestamp > ?
            GROUP BY model_name
            ORDER BY total_queries DESC
        ''', (since,))
        
        results = cursor.fetchall()
        conn.close()
        
        analysis = {}
        for row in results:
            model_name, total, avg_time, avg_rating, satisfaction = row
            analysis[model_name] = {
                'total_queries': total,
                'avg_response_time': avg_time,
                'avg_rating': avg_rating if avg_rating else 0,
                'satisfaction_rate': satisfaction if satisfaction else 0
            }
        
        return analysis
    
    def evolve_generation(self) -> Dict:
        """
        Evolve ke generasi berikutnya
        """
        print("="*70)
        print("KUWERA EVOLUTION ENGINE")
        print("="*70)
        print()
        
        # Analyze current performance
        performance = self.analyze_performance(days=7)
        
        if not performance:
            print("[WARNING] Not enough data for evolution")
            return {'status': 'insufficient_data'}
        
        print(f"Generation: {self.evolution_state['generation']}")
        print(f"Total Interactions: {self.evolution_state['total_interactions']}")
        print()
        
        # Calculate improvements
        improvements = []
        best_model = None
        best_score = -999
        
        print("MODEL PERFORMANCE:")
        print("-"*70)
        
        for model_name, metrics in performance.items():
            # Calculate composite score
            score = (
                metrics['satisfaction_rate'] * 0.4 +
                (5 - min(metrics['avg_response_time'], 5)) * 10 * 0.3 +
                (metrics['avg_rating'] if metrics['avg_rating'] else 3) * 10 * 0.3
            )
            
            print(f"{model_name}:")
            print(f"  Queries: {metrics['total_queries']}")
            print(f"  Avg Time: {metrics['avg_response_time']:.2f}s")
            print(f"  Avg Rating: {metrics['avg_rating']:.2f}/5")
            print(f"  Satisfaction: {metrics['satisfaction_rate']:.1f}%")
            print(f"  Score: {score:.2f}")
            print()
            
            if score > best_score:
                best_score = score
                best_model = model_name
            
            # Track improvements
            if score > 70:
                improvements.append(f"{model_name} performing excellently")
            elif metrics['avg_response_time'] > 5:
                improvements.append(f"{model_name} needs optimization")
        
        # Update generation
        self.evolution_state['generation'] += 1
        
        # Log evolution
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO evolution_history 
            (timestamp, generation, best_model, avg_performance, changes_made)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            self.evolution_state['generation'],
            best_model,
            best_score,
            json.dumps(improvements)
        ))
        
        conn.commit()
        conn.close()
        
        self.evolution_state['last_evolution'] = datetime.now().isoformat()
        self._save_evolution_state()
        
        print("="*70)
        print("EVOLUTION COMPLETE")
        print("="*70)
        print(f"Best Model: {best_model} (Score: {best_score:.2f})")
        print(f"New Generation: {self.evolution_state['generation']}")
        print()
        print("Improvements:")
        for imp in improvements:
            print(f"  • {imp}")
        print("="*70)
        
        return {
            'generation': self.evolution_state['generation'],
            'best_model': best_model,
            'best_score': best_score,
            'improvements': improvements
        }
    
    def get_model_recommendation(self, query_type: str = "general") -> str:
        """Get model recommendation berdasarkan evolution data"""
        weights = self.evolution_state['model_weights']
        
        if not weights:
            return None
        
        # Return model dengan weight tertinggi untuk query type tersebut
        best_model = max(weights, key=weights.get)
        return best_model
    
    def generate_report(self) -> str:
        """Generate evolution report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get overall stats
        cursor.execute('SELECT COUNT(*) FROM interactions')
        total_interactions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT model_name) FROM interactions')
        total_models = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(user_rating) FROM interactions WHERE user_rating > 0')
        avg_rating = cursor.fetchone()[0] or 0
        
        # Get evolution history
        cursor.execute('SELECT * FROM evolution_history ORDER BY timestamp DESC LIMIT 5')
        evolution_history = cursor.fetchall()
        
        conn.close()
        
        lines = []
        lines.append("="*70)
        lines.append("KUWERA EVOLUTION REPORT")
        lines.append("="*70)
        lines.append("")
        lines.append(f"Generation: {self.evolution_state['generation']}")
        lines.append(f"Total Interactions: {total_interactions}")
        lines.append(f"Active Models: {total_models}")
        lines.append(f"Average Rating: {avg_rating:.2f}/5")
        lines.append("")
        
        if evolution_history:
            lines.append("EVOLUTION HISTORY:")
            lines.append("-"*70)
            for gen in evolution_history:
                lines.append(f"Gen {gen[3]}: {gen[4]} (Score: {gen[5]:.2f})")
        
        lines.append("")
        lines.append("MODEL WEIGHTS:")
        lines.append("-"*70)
        for model, weight in sorted(self.evolution_state['model_weights'].items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(weight)
            lines.append(f"  {model:20} {bar} {weight:.2f}")
        
        lines.append("="*70)
        
        return "\n".join(lines)


def main():
    """Test evolution engine"""
    engine = EvolutionEngine()
    
    print(engine.generate_report())
    print()
    
    # Run evolution
    result = engine.evolve_generation()
    
    if result['status'] != 'insufficient_data':
        print()
        print(f"Recommendation: Use {result['best_model']} for best results")


if __name__ == "__main__":
    main()
