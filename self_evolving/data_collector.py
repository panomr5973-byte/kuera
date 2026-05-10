#!/usr/bin/env python
"""
Data Collector - Sistem logging interaksi user untuk self-improvement
Menyimpan feedback dan metadata ke SQLite untuk analisis berkelanjutan
"""

import sqlite3
import json
import datetime
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class DataCollector:
    """
    Kelas untuk mengumpulkan dan menyimpan data interaksi user.
    Menyimpan ke SQLite dengan skema yang extensible.
    """
    
    def __init__(self, db_path: str = "logs/feedback/self_improve.db"):
        """
        Initialize DataCollector dengan database SQLite
        
        Args:
            db_path: Path ke SQLite database
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        logger.info(f"[OK] DataCollector initialized: {db_path}")
    
    def _init_tables(self):
        """Inisialisasi tabel database"""
        # Tabel utama untuk interaksi
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                user_input TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                model_used TEXT,
                user_feedback INTEGER,  -- 1: good, 0: bad, NULL: no feedback
                feedback_reason TEXT,   -- Alasan feedback (jika ada)
                metadata TEXT,          -- JSON string untuk data tambahan
                latency_ms REAL,        -- Waktu respons dalam ms
                confidence REAL         -- Confidence score prediksi
            )
        """)
        
        # Tabel untuk metrics per model
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                dataset_version TEXT
            )
        """)
        
        # Tabel untuk drift detection history
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS drift_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                feature_name TEXT,
                drift_score REAL,
                drift_detected BOOLEAN,
                threshold REAL
            )
        """)
        
        self.conn.commit()
    
    def log_interaction(
        self,
        user_input: str,
        ai_response: str,
        model_used: str = "unknown",
        user_feedback: Optional[int] = None,
        feedback_reason: Optional[str] = None,
        session_id: Optional[str] = None,
        latency_ms: Optional[float] = None,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log satu interaksi user-AI
        
        Returns:
            ID dari record yang baru dibuat
        """
        cursor = self.conn.execute(
            """INSERT INTO interactions 
               (timestamp, session_id, user_input, ai_response, model_used,
                user_feedback, feedback_reason, metadata, latency_ms, confidence)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.datetime.now().isoformat(),
                session_id,
                user_input,
                ai_response,
                model_used,
                user_feedback,
                feedback_reason,
                json.dumps(metadata) if metadata else None,
                latency_ms,
                confidence
            )
        )
        self.conn.commit()
        logger.debug(f"[OK] Logged interaction #{cursor.lastrowid}")
        return cursor.lastrowid
    
    def update_feedback(
        self,
        interaction_id: int,
        feedback: int,
        reason: Optional[str] = None
    ):
        """Update feedback untuk interaksi yang sudah ada"""
        self.conn.execute(
            "UPDATE interactions SET user_feedback = ?, feedback_reason = ? WHERE id = ?",
            (feedback, reason, interaction_id)
        )
        self.conn.commit()
        logger.info(f"[OK] Updated feedback for interaction #{interaction_id}")
    
    def get_recent_interactions(
        self,
        hours: int = 24,
        with_feedback_only: bool = False
    ) -> List[Dict]:
        """
        Ambil interaksi dalam rentang waktu tertentu
        
        Args:
            hours: Jumlah jam ke belakang
            with_feedback_only: Hanya ambil yang punya feedback
        """
        since = (datetime.datetime.now() - datetime.timedelta(hours=hours)).isoformat()
        
        query = "SELECT * FROM interactions WHERE timestamp > ?"
        params = [since]
        
        if with_feedback_only:
            query += " AND user_feedback IS NOT NULL"
        
        query += " ORDER BY timestamp DESC"
        
        cursor = self.conn.execute(query, params)
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            data = dict(row)
            if data['metadata']:
                data['metadata'] = json.loads(data['metadata'])
            result.append(data)
        
        return result
    
    def get_feedback_stats(self, hours: int = 24) -> Dict:
        """Get statistics feedback dalam periode tertentu"""
        since = (datetime.datetime.now() - datetime.timedelta(hours=hours)).isoformat()
        
        cursor = self.conn.execute(
            """SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN user_feedback = 1 THEN 1 ELSE 0 END) as positive,
                SUM(CASE WHEN user_feedback = 0 THEN 1 ELSE 0 END) as negative,
                AVG(latency_ms) as avg_latency
            FROM interactions 
            WHERE timestamp > ? AND user_feedback IS NOT NULL""",
            [since]
        )
        
        row = cursor.fetchone()
        return {
            'total_feedback': row[0] or 0,
            'positive': row[1] or 0,
            'negative': row[2] or 0,
            'satisfaction_rate': (row[1] / (row[1] + row[2]) * 100) if (row[1] + row[2]) > 0 else 0,
            'avg_latency_ms': row[3] or 0
        }
    
    def export_training_data(
        self,
        output_path: str,
        min_feedback_score: int = 1,
        hours: Optional[int] = None
    ) -> int:
        """
        Export data dengan feedback positif untuk training ulang
        
        Returns:
            Jumlah records yang diexport
        """
        import pandas as pd
        
        if hours:
            since = (datetime.datetime.now() - datetime.timedelta(hours=hours)).isoformat()
            query = """SELECT * FROM interactions 
                      WHERE user_feedback >= ? AND timestamp > ?"""
            params = [min_feedback_score, since]
        else:
            query = "SELECT * FROM interactions WHERE user_feedback >= ?"
            params = [min_feedback_score]
        
        df = pd.read_sql_query(query, self.conn, params=params)
        
        if len(df) > 0:
            df.to_csv(output_path, index=False)
            logger.info(f"[OK] Exported {len(df)} records to {output_path}")
        
        return len(df)
    
    def log_model_metric(
        self,
        model_id: str,
        metric_name: str,
        metric_value: float,
        dataset_version: Optional[str] = None
    ):
        """Log metric performa model"""
        self.conn.execute(
            """INSERT INTO model_metrics 
               (timestamp, model_id, metric_name, metric_value, dataset_version)
               VALUES (?, ?, ?, ?, ?)""",
            (datetime.datetime.now().isoformat(), model_id, metric_name, metric_value, dataset_version)
        )
        self.conn.commit()
    
    def get_model_metrics(
        self,
        model_id: Optional[str] = None,
        metric_name: Optional[str] = None
    ) -> List[Dict]:
        """Get history metrics untuk satu atau semua model"""
        query = "SELECT * FROM model_metrics WHERE 1=1"
        params = []
        
        if model_id:
            query += " AND model_id = ?"
            params.append(model_id)
        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)
        
        query += " ORDER BY timestamp DESC"
        
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        logger.info("[OK] DataCollector closed")


if __name__ == '__main__':
    # Test DataCollector
    logging.basicConfig(level=logging.INFO)
    
    collector = DataCollector()
    
    # Test log interaction
    id1 = collector.log_interaction(
        user_input="Apa itu machine learning?",
        ai_response="Machine learning adalah cabang AI...",
        model_used="llama3.2",
        confidence=0.95,
        latency_ms=120.5
    )
    
    # Update feedback
    collector.update_feedback(id1, feedback=1, reason="Jawaban bagus")
    
    # Get stats
    stats = collector.get_feedback_stats(hours=24)
    print(f"Stats: {stats}")
    
    # Get recent interactions
    recent = collector.get_recent_interactions(hours=24)
    print(f"Recent interactions: {len(recent)}")
    
    collector.close()
