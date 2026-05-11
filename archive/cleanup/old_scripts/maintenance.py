#!/usr/bin/env python3
"""
KUERA Maintenance Scheduler
Self-Sustaining AI System - Anti-Information Starvation

Features:
1. Auto-update knowledge base
2. Continual learning
3. Active learning
4. Health monitoring
5. Backup & recovery
"""

import os
import sys
import json
import time
import shutil
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("[WARNING] schedule not installed. Run: pip install schedule")

# Add self_evolving to path
sys.path.insert(0, str(Path(__file__).parent / 'self_evolving'))

from self_evolving.trainer import SelfImprovementTrainer
from self_evolving.retrainer import SelfRetrainer, RetrainConfig


class KnowledgeRefresher:
    """
    Anti-Information Starvation: Auto-refresh knowledge base
    """
    
    KNOWLEDGE_DIR = Path("data/knowledge/")
    EXTERNAL_DIR = Path("data/external/")
    
    def __init__(self):
        self.KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        self.EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
        
        # Track last update
        self.state_file = Path("data/knowledge_state.json")
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {'last_refresh': None, 'doc_count': 0}
    
    def _save_state(self):
        self.state['last_refresh'] = datetime.now().isoformat()
        self.state['doc_count'] = len(list(self.KNOWLEDGE_DIR.glob("*.txt")))
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def refresh_knowledge(self) -> Dict:
        """
        Refresh knowledge base
        - Check for new files
        - Update freshness scores
        - Archive old versions
        """
        print("[Knowledge] Refreshing knowledge base...")
        
        stats = {
            'new_docs': 0,
            'updated': 0,
            'archived': 0,
            'errors': []
        }
        
        try:
            # 1. Check external feeds (simulated - in real app, parse RSS)
            self._check_external_sources()
            
            # 2. Archive old knowledge (older than 6 months)
            self._archive_old_knowledge()
            
            # 3. Load high-quality feedback sebagai knowledge baru
            self._feedback_to_knowledge()
            
            # 4. Update metadata
            self._save_state()
            
            print(f"[Knowledge] Refresh complete: {stats}")
            return stats
            
        except Exception as e:
            print(f"[Knowledge] Error: {e}")
            stats['errors'].append(str(e))
            return stats
    
    def _check_external_sources(self):
        """Check dan download external sources (placeholder)"""
        # In real implementation:
        # - Parse RSS feeds (arxiv, news, etc)
        # - Download dan cache
        # - Extract text
        pass
    
    def _archive_old_knowledge(self):
        """Archive knowledge older than 6 months"""
        archive_dir = self.KNOWLEDGE_DIR / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        cutoff = datetime.now() - timedelta(days=180)
        
        for file_path in self.KNOWLEDGE_DIR.glob("*.txt"):
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff:
                # Archive
                shutil.move(str(file_path), str(archive_dir / file_path.name))
                print(f"[Knowledge] Archived: {file_path.name}")
    
    def _feedback_to_knowledge(self):
        """Convert high-quality feedback ke knowledge base"""
        try:
            db_path = "data/kuera_database.db"
            if not os.path.exists(db_path):
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get recent high-quality interactions
            cursor.execute("""
                SELECT user_message, kuera_response, created_at
                FROM interactions
                WHERE user_feedback = 1 
                   OR (confidence > 0.9 AND LENGTH(kuera_response) > 100)
                ORDER BY created_at DESC
                LIMIT 50
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            # Save sebagai knowledge baru
            for i, (q, a, date) in enumerate(rows[:20], 1):
                content = f"Q: {q}\nA: {a}\nDate: {date}"
                filename = f"feedback_qa_{datetime.now().strftime('%Y%m')}_{i:03d}.txt"
                
                filepath = self.KNOWLEDGE_DIR / filename
                if not filepath.exists():
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
            
            print(f"[Knowledge] Added {len(rows[:20])} feedback entries.")
            
        except Exception as e:
            print(f"[Knowledge] Feedback conversion error: {e}")
    
    def get_freshness_report(self) -> Dict:
        """Report freshness dari knowledge base"""
        files = list(self.KNOWLEDGE_DIR.glob("*.txt"))
        
        now = datetime.now()
        fresh_count = 0  # < 30 days
        stale_count = 0  # > 90 days
        
        for f in files:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            age_days = (now - mtime).days
            
            if age_days < 30:
                fresh_count += 1
            elif age_days > 90:
                stale_count += 1
        
        return {
            'total_docs': len(files),
            'fresh_docs': fresh_count,
            'stale_docs': stale_count,
            'freshness_ratio': fresh_count / max(len(files), 1),
            'last_refresh': self.state.get('last_refresh')
        }


class HealthMonitor:
    """
    Self-Diagnose: Monitor kesehatan sistem AI
    """
    
    def __init__(self, db_path: str = "data/kuera_database.db"):
        self.db_path = db_path
        self.health_log = Path("data/health_log.json")
    
    def check_health(self) -> Dict:
        """
        Comprehensive health check
        """
        print("[Health] Running diagnostics...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {},
            'alerts': []
        }
        
        # 1. Check usage
        usage = self._check_usage()
        report['checks']['usage'] = usage
        
        if usage['daily_interactions'] < 10:
            report['alerts'].append("Low usage detected - consider active learning")
            report['status'] = 'warning'
        
        # 2. Check satisfaction
        satisfaction = self._check_satisfaction()
        report['checks']['satisfaction'] = satisfaction
        
        if satisfaction['avg_feedback'] < 0.7:
            report['alerts'].append("Low satisfaction - retraining recommended")
            report['status'] = 'critical'
        
        # 3. Check model freshness
        models = self._check_models()
        report['checks']['models'] = models
        
        if models['days_since_update'] > 30:
            report['alerts'].append("Models stale - retrain needed")
            report['status'] = 'warning'
        
        # 4. Check database
        db_health = self._check_database()
        report['checks']['database'] = db_health
        
        # Save log
        self._save_health_log(report)
        
        return report
    
    def _check_usage(self) -> Dict:
        """Check usage metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Last 24 hours
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM interactions 
                WHERE created_at > ?
            """, (yesterday,))
            daily = cursor.fetchone()[0]
            
            # Last 7 days
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM interactions 
                WHERE created_at > ?
            """, (week_ago,))
            weekly = cursor.fetchone()[0]
            
            # Unique users
            cursor.execute("SELECT COUNT(DISTINCT session_id) FROM interactions")
            unique_users = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'daily_interactions': daily,
                'weekly_interactions': weekly,
                'unique_users': unique_users,
                'trend': 'up' if weekly > daily * 5 else 'stable'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _check_satisfaction(self) -> Dict:
        """Check user satisfaction metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT AVG(user_feedback), COUNT(*) 
                FROM interactions 
                WHERE user_feedback IS NOT NULL
            """)
            result = cursor.fetchone()
            conn.close()
            
            avg_feedback = result[0] if result[0] else 0.5
            count = result[1]
            
            return {
                'avg_feedback': round(avg_feedback, 2),
                'feedback_count': count,
                'status': 'good' if avg_feedback > 0.7 else 'needs_improvement'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _check_models(self) -> Dict:
        """Check model status"""
        try:
            models_dir = Path("models/")
            if not models_dir.exists():
                return {'error': 'Models directory not found'}
            
            # Find latest model
            model_files = list(models_dir.glob("*.pkl"))
            if not model_files:
                return {'status': 'no_models'}
            
            latest = max(model_files, key=lambda p: p.stat().st_mtime)
            mtime = datetime.fromtimestamp(latest.stat().st_mtime)
            age_days = (datetime.now() - mtime).days
            
            return {
                'latest_model': latest.name,
                'last_update': mtime.isoformat(),
                'days_since_update': age_days,
                'status': 'fresh' if age_days < 7 else 'stale' if age_days > 30 else 'ok'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _check_database(self) -> Dict:
        """Check database health"""
        try:
            if not os.path.exists(self.db_path):
                return {'status': 'missing'}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]
            
            # Check size
            size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
            
            conn.close()
            
            return {
                'tables': tables,
                'size_mb': round(size_mb, 2),
                'status': 'healthy'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _save_health_log(self, report: Dict):
        """Save health report ke log"""
        try:
            logs = []
            if self.health_log.exists():
                with open(self.health_log, 'r') as f:
                    logs = json.load(f)
            
            logs.append(report)
            
            # Keep only last 30 logs
            logs = logs[-30:]
            
            with open(self.health_log, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"[Health] Log save error: {e}")


class ActiveLearning:
    """
    AI minta bantuan saat bingung - jaga engagement
    """
    
    def __init__(self, db_path: str = "data/kuera_database.db"):
        self.db_path = db_path
    
    def get_uncertain_queries(self, hours: int = 24, limit: int = 5) -> List[Dict]:
        """
        Get queries dengan low confidence untuk ditanyakan ke user
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT id, user_message, kuera_response, confidence
                FROM interactions
                WHERE created_at > ?
                  AND confidence < 0.5
                  AND (user_feedback IS NULL OR user_feedback = 0)
                ORDER BY confidence ASC
                LIMIT ?
            """, (since, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'query': row[1],
                    'response': row[2],
                    'confidence': row[3]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"[ActiveLearning] Error: {e}")
            return []
    
    def suggest_learning_questions(self) -> List[str]:
        """Suggest questions untuk ditanyakan ke user"""
        uncertain = self.get_uncertain_queries()
        
        suggestions = []
        for item in uncertain:
            suggestions.append(f"Bagaimana cara menjawab: '{item['query'][:50]}...'?")
        
        return suggestions


class BackupManager:
    """
    Backup & Recovery - AI yang abadi
    """
    
    BACKUP_DIR = Path("backup/")
    
    def __init__(self):
        self.BACKUP_DIR.mkdir(exist_ok=True)
    
    def backup_all(self) -> Dict:
        """
        Full backup: models + database + config
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.BACKUP_DIR / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        stats = {'backed_up': [], 'errors': []}
        
        # 1. Backup database
        try:
            db_backup = backup_path / "database"
            db_backup.mkdir(exist_ok=True)
            
            if os.path.exists("data/kuera_database.db"):
                shutil.copy("data/kuera_database.db", db_backup / "kuera_database.db")
                stats['backed_up'].append('database')
        except Exception as e:
            stats['errors'].append(f'database: {e}')
        
        # 2. Backup models
        try:
            models_backup = backup_path / "models"
            models_backup.mkdir(exist_ok=True)
            
            if os.path.exists("models/"):
                for model_file in Path("models/").glob("*.pkl"):
                    shutil.copy(model_file, models_backup / model_file.name)
                stats['backed_up'].append('models')
        except Exception as e:
            stats['errors'].append(f'models: {e}')
        
        # 3. Backup knowledge
        try:
            kb_backup = backup_path / "knowledge"
            kb_backup.mkdir(exist_ok=True)
            
            if os.path.exists("data/knowledge/"):
                for kb_file in Path("data/knowledge/").glob("*.txt"):
                    shutil.copy(kb_file, kb_backup / kb_file.name)
                stats['backed_up'].append('knowledge')
        except Exception as e:
            stats['errors'].append(f'knowledge: {e}')
        
        # 4. Backup config
        try:
            config_files = ['config.py', 'self_improve.db', 'feedback/']
            for cf in config_files:
                if os.path.exists(cf):
                    if os.path.isfile(cf):
                        shutil.copy(cf, backup_path / cf)
                    elif os.path.isdir(cf):
                        shutil.copytree(cf, backup_path / cf, dirs_exist_ok=True)
            stats['backed_up'].append('config')
        except Exception as e:
            stats['errors'].append(f'config: {e}')
        
        print(f"[Backup] Complete: {stats}")
        return stats
    
    def list_backups(self) -> List[Dict]:
        """List available backups"""
        backups = []
        for backup_dir in sorted(self.BACKUP_DIR.glob("backup_*"), reverse=True):
            mtime = datetime.fromtimestamp(backup_dir.stat().st_mtime)
            backups.append({
                'name': backup_dir.name,
                'date': mtime.isoformat(),
                'age_days': (datetime.now() - mtime).days,
                'path': str(backup_dir)
            })
        return backups
    
    def restore(self, backup_name: str) -> bool:
        """Restore dari backup"""
        backup_path = self.BACKUP_DIR / backup_name
        
        if not backup_path.exists():
            print(f"[Restore] Backup not found: {backup_name}")
            return False
        
        try:
            # Restore database
            db_backup = backup_path / "database" / "kuera_database.db"
            if db_backup.exists():
                shutil.copy(db_backup, "data/kuera_database.db")
                print("[Restore] Database restored.")
            
            # Restore models
            models_backup = backup_path / "models"
            if models_backup.exists():
                for model_file in models_backup.glob("*.pkl"):
                    shutil.copy(model_file, "models/")
                print("[Restore] Models restored.")
            
            print(f"[Restore] Complete from {backup_name}")
            return True
            
        except Exception as e:
            print(f"[Restore] Error: {e}")
            return False


class MaintenanceScheduler:
    """
    Main scheduler untuk maintenance harian
    """
    
    def __init__(self):
        self.knowledge = KnowledgeRefresher()
        self.health = HealthMonitor()
        self.active_learning = ActiveLearning()
        self.backup = BackupManager()
        
        self.running = False
    
    def daily_maintenance(self):
        """Run all daily maintenance tasks"""
        print("\n" + "="*70)
        print(f"[Maintenance] Daily maintenance started: {datetime.now()}")
        print("="*70)
        
        # 1. Health check
        print("\n[1/5] Health Check...")
        health_report = self.health.check_health()
        print(f"Status: {health_report['status']}")
        if health_report['alerts']:
            for alert in health_report['alerts']:
                print(f"  ALERT: {alert}")
        
        # 2. Knowledge refresh
        print("\n[2/5] Knowledge Refresh...")
        refresh_stats = self.knowledge.refresh_knowledge()
        freshness = self.knowledge.get_freshness_report()
        print(f"Freshness ratio: {freshness['freshness_ratio']:.1%}")
        
        # 3. Check active learning needs
        print("\n[3/5] Active Learning Check...")
        uncertain = self.active_learning.get_uncertain_queries()
        if uncertain:
            print(f"Found {len(uncertain)} uncertain queries for review")
        
        # 4. Backup
        print("\n[4/5] Backup...")
        backup_stats = self.backup.backup_all()
        print(f"Backed up: {backup_stats['backed_up']}")
        
        # 5. Check if retraining needed
        print("\n[5/5] Retrain Check...")
        if health_report['status'] in ['critical', 'warning']:
            print("Retraining recommended!")
            # Trigger retrain
            self._trigger_retrain()
        else:
            print("Models healthy - no retrain needed.")
        
        print("\n" + "="*70)
        print("[Maintenance] Daily maintenance complete!")
        print("="*70 + "\n")
    
    def _trigger_retrain(self):
        """Trigger model retraining"""
        try:
            config = RetrainConfig(threshold_samples=100)
            retrainer = SelfRetrainer(config)
            retrainer.run_retraining_cycle()
        except Exception as e:
            print(f"[Retrain] Error: {e}")
    
    def schedule_jobs(self):
        """Schedule semua maintenance jobs"""
        if not SCHEDULE_AVAILABLE:
            print("[Scheduler] schedule library not available.")
            return
        
        # Daily at 2 AM
        schedule.every().day.at("02:00").do(self.daily_maintenance)
        
        # Health check every 6 hours
        schedule.every(6).hours.do(self.health.check_health)
        
        # Backup every 12 hours
        schedule.every(12).hours.do(self.backup.backup_all)
        
        print("[Scheduler] Jobs scheduled:")
        print("  - Daily maintenance: 02:00")
        print("  - Health check: every 6 hours")
        print("  - Backup: every 12 hours")
    
    def run_scheduler(self):
        """Run scheduler loop"""
        if not SCHEDULE_AVAILABLE:
            print("[Scheduler] Cannot run - schedule not installed.")
            return
        
        self.schedule_jobs()
        self.running = True
        
        print("\n[Scheduler] Running... Press Ctrl+C to stop.\n")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n[Scheduler] Stopped.")
            self.running = False
    
    def run_once(self):
        """Run maintenance sekali (tanpa scheduler)"""
        self.daily_maintenance()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KUERA Maintenance Scheduler')
    parser.add_argument('--schedule', action='store_true', help='Run scheduler')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--backup', action='store_true', help='Backup only')
    parser.add_argument('--health', action='store_true', help='Health check only')
    parser.add_argument('--knowledge', action='store_true', help='Refresh knowledge only')
    
    args = parser.parse_args()
    
    scheduler = MaintenanceScheduler()
    
    if args.schedule:
        scheduler.run_scheduler()
    elif args.once:
        scheduler.run_once()
    elif args.backup:
        scheduler.backup.backup_all()
    elif args.health:
        report = scheduler.health.check_health()
        print(json.dumps(report, indent=2))
    elif args.knowledge:
        scheduler.knowledge.refresh_knowledge()
        print(json.dumps(scheduler.knowledge.get_freshness_report(), indent=2))
    else:
        # Default: run once
        scheduler.run_once()


if __name__ == "__main__":
    main()
