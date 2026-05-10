#!/usr/bin/env python
"""
AutoRetrain - Sistem retraining otomatis dengan scheduling
Menjalankan retraining berdasarkan trigger (schedule, drift, atau performance drop)
"""

import os
import sys
import json
import time
import logging
import pickle
import sqlite3
from typing import Dict, List, Optional, Callable
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

import schedule
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

# Optional imports
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class RetrainConfig:
    """Configuration untuk auto-retraining"""
    min_samples: int = 100           # Minimum data baru untuk retrain
    check_interval_hours: int = 24   # Interval pengecekan
    performance_threshold: float = 0.05  # Drop threshold untuk trigger retrain
    max_models_to_keep: int = 5      # Jumlah model history yang disimpan
    test_size: float = 0.2
    random_state: int = 42


class AutoRetrain:
    """
    Sistem auto-retraining dengan berbagai trigger:
    1. Scheduled (periodic)
    2. Performance-based (jika metrics turun)
    3. Data-based (jika ada cukup data baru)
    """
    
    def __init__(
        self,
        config: RetrainConfig,
        db_path: str = "logs/feedback/self_improve.db",
        models_dir: str = "models",
        reference_data_path: Optional[str] = None
    ):
        self.config = config
        self.db_path = db_path
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.reference_data_path = reference_data_path
        
        # Model registry
        self.model_registry_path = self.models_dir / "model_registry.json"
        self.model_registry = self._load_registry()
        
        # Training history
        self.training_history: List[Dict] = []
        
        logger.info(f"[OK] AutoRetrain initialized")
        logger.info(f"    Config: {asdict(config)}")
    
    def _load_registry(self) -> Dict:
        """Load model registry dari JSON"""
        if self.model_registry_path.exists():
            with open(self.model_registry_path) as f:
                return json.load(f)
        return {
            'models': [],
            'current_production': None,
            'baseline_metrics': {}
        }
    
    def _save_registry(self):
        """Save model registry ke JSON"""
        with open(self.model_registry_path, 'w') as f:
            json.dump(self.model_registry, f, indent=2)
    
    def get_new_training_data(self, since_hours: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Ambil data baru dari database untuk training
        
        Returns:
            DataFrame dengan data baru atau None jika tidak cukup
        """
        if not Path(self.db_path).exists():
            logger.warning(f"Database not found: {self.db_path}")
            return None
        
        conn = sqlite3.connect(self.db_path)
        
        if since_hours:
            since = (datetime.now() - timedelta(hours=since_hours)).isoformat()
            query = """
                SELECT * FROM interactions 
                WHERE timestamp > ? AND user_feedback IS NOT NULL
            """
            df = pd.read_sql_query(query, conn, params=[since])
        else:
            query = "SELECT * FROM interactions WHERE user_feedback IS NOT NULL"
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        if len(df) < self.config.min_samples:
            logger.info(f"Not enough new data: {len(df)} < {self.config.min_samples}")
            return None
        
        logger.info(f"[OK] Retrieved {len(df)} new training samples")
        return df
    
    def prepare_training_data(self, feedback_data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data dari feedback untuk training
        
        Transformasi:
        - Konversi user_input ke features (simplified)
        - user_feedback menjadi target
        """
        # Simplified: Buat synthetic features dari metadata
        # Dalam implementasi nyata, ini akan menggunakan embedding/vectorization
        
        training_records = []
        
        for _, row in feedback_data.iterrows():
            # Extract features dari metadata jika ada
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            
            record = {
                'input_length': len(row['user_input']),
                'response_length': len(row['ai_response']),
                'confidence': row['confidence'] or 0.5,
                'latency_ms': row['latency_ms'] or 100,
                'model_used': hash(row['model_used']) % 100,  # Encode categorical
                'hour_of_day': pd.to_datetime(row['timestamp']).hour,
                'target': row['user_feedback']  # 0 atau 1
            }
            
            # Add metadata features
            for key, value in metadata.items():
                if isinstance(value, (int, float)):
                    record[f'meta_{key}'] = value
            
            training_records.append(record)
        
        return pd.DataFrame(training_records)
    
    def train_model(
        self,
        train_df: pd.DataFrame,
        model_type: str = "auto",
        model_id: Optional[str] = None
    ) -> Dict:
        """
        Train model baru dengan data terbaru
        
        Args:
            train_df: DataFrame untuk training
            model_type: 'rf', 'gb', 'lr', atau 'auto' (pilih terbaik)
            model_id: Identifier untuk model
        
        Returns:
            Dictionary dengan hasil training
        """
        if model_id is None:
            model_id = f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Split features/target
        X = train_df.drop(columns=['target'])
        y = train_df['target']
        
        # Check if we have at least 2 classes
        unique_classes = y.unique()
        if len(unique_classes) < 2:
            logger.error(f"[ERROR] Need at least 2 classes, got {len(unique_classes)}: {unique_classes}")
            return {
                'error': f'Only {len(unique_classes)} class(es) in data. Need both 0 and 1.',
                'model_id': None
            }
        
        # Handle any NaN values
        X = X.fillna(X.mean())
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=self.config.test_size, 
            random_state=self.config.random_state
        )
        
        # Define models
        models = {
            'rf': RandomForestClassifier(n_estimators=100, random_state=42),
            'gb': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'lr': LogisticRegression(max_iter=1000, random_state=42)
        }
        
        if model_type == "auto":
            # Train semua dan pilih terbaik
            best_score = 0
            best_model = None
            best_type = None
            
            for mtype, model in models.items():
                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)
                score = f1_score(y_val, y_pred, average='weighted')
                
                logger.info(f"  {mtype}: F1={score:.4f}")
                
                if score > best_score:
                    best_score = score
                    best_model = model
                    best_type = mtype
            
            model = best_model
            model_type = best_type
            final_score = best_score
        else:
            model = models[model_type]
            model.fit(X_train, y_train)
            y_pred = model.predict(X_val)
            final_score = f1_score(y_val, y_pred, average='weighted')
        
        # Save model
        model_path = self.models_dir / f"{model_id}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Calculate metrics
        y_pred = model.predict(X_val)
        metrics = {
            'accuracy': accuracy_score(y_val, y_pred),
            'f1_score': final_score,
            'n_samples': len(train_df),
            'n_features': X.shape[1]
        }
        
        # Log ke MLflow
        if MLFLOW_AVAILABLE:
            with mlflow.start_run(run_name=f"retrain_{model_id}"):
                mlflow.log_params({
                    'model_type': model_type,
                    'n_samples': len(train_df),
                    'n_features': X.shape[1]
                })
                mlflow.log_metrics(metrics)
                mlflow.sklearn.log_model(model, model_id)
        
        # Update registry
        model_info = {
            'model_id': model_id,
            'model_type': model_type,
            'model_path': str(model_path),
            'created_at': datetime.now().isoformat(),
            'metrics': metrics,
            'n_samples': len(train_df)
        }
        
        self.model_registry['models'].append(model_info)
        self._save_registry()
        
        logger.info(f"[OK] Trained {model_type} model: {model_id}")
        logger.info(f"    Metrics: {metrics}")
        
        return {
            'model_id': model_id,
            'model_path': str(model_path),
            'model_type': model_type,
            'metrics': metrics
        }
    
    def check_and_trigger_retrain(self, force: bool = False) -> Optional[Dict]:
        """
        Cek kondisi dan trigger retraining jika perlu
        
        Returns:
            Hasil training jika di-trigger, None jika tidak
        """
        logger.info("[CHECK] Checking retrain conditions...")
        
        # Check 1: Cukup data baru?
        new_data = self.get_new_training_data(since_hours=24)
        
        if new_data is None and not force:
            logger.info("[SKIP] Not enough new data for retraining")
            return None
        
        # Prepare data
        train_df = self.prepare_training_data(new_data)
        
        # Train model
        result = self.train_model(train_df, model_type="auto")
        
        # Log training
        self.training_history.append({
            'timestamp': datetime.now().isoformat(),
            'trigger': 'scheduled' if not force else 'manual',
            'result': result
        })
        
        return result
    
    def schedule_retrain(self):
        """Setup scheduled retraining"""
        logger.info(f"[OK] Scheduling retrain every {self.config.check_interval_hours} hours")
        
        schedule.every(self.config.check_interval_hours).hours.do(
            self.check_and_trigger_retrain
        )
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("[OK] Stopping scheduler")
    
    def promote_to_production(self, model_id: str) -> bool:
        """
        Promote model ke production
        
        Args:
            model_id: ID model yang akan dipromosikan
        """
        # Find model in registry
        model_info = None
        for m in self.model_registry['models']:
            if m['model_id'] == model_id:
                model_info = m
                break
        
        if not model_info:
            logger.error(f"Model not found: {model_id}")
            return False
        
        # Update production pointer
        old_production = self.model_registry.get('current_production')
        self.model_registry['current_production'] = model_id
        self.model_registry['baseline_metrics'] = model_info['metrics']
        self._save_registry()
        
        logger.info(f"[OK] Promoted {model_id} to production")
        logger.info(f"    Previous: {old_production}")
        
        return True
    
    def rollback(self) -> bool:
        """Rollback ke model sebelumnya"""
        models = self.model_registry['models']
        if len(models) < 2:
            logger.warning("No previous model to rollback to")
            return False
        
        # Get second to last model
        previous = models[-2]['model_id']
        return self.promote_to_production(previous)
    
    def get_production_model(self) -> Optional[Dict]:
        """Get info model yang sedang di production"""
        prod_id = self.model_registry.get('current_production')
        if not prod_id:
            return None
        
        for m in self.model_registry['models']:
            if m['model_id'] == prod_id:
                return m
        return None


def run_scheduler_forever():
    """Entry point untuk menjalankan scheduler di background"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = RetrainConfig(
        min_samples=50,
        check_interval_hours=1  # Setiap jam untuk testing
    )
    
    retrainer = AutoRetrain(config=config)
    
    logger.info("="*60)
    logger.info("STARTING AUTO-RETRAIN SCHEDULER")
    logger.info("="*60)
    
    retrainer.schedule_retrain()


if __name__ == '__main__':
    # Test AutoRetrain
    logging.basicConfig(level=logging.INFO)
    
    config = RetrainConfig(min_samples=10, check_interval_hours=24)
    retrainer = AutoRetrain(config=config)
    
    # Create synthetic feedback data untuk test
    test_feedback = pd.DataFrame({
        'user_input': ['q1', 'q2', 'q3', 'q4', 'q5'] * 4,
        'ai_response': ['a1', 'a2', 'a3', 'a4', 'a5'] * 4,
        'user_feedback': [1, 0, 1, 1, 0] * 4,
        'timestamp': [datetime.now().isoformat()] * 20,
        'confidence': [0.9] * 20,
        'latency_ms': [100] * 20,
        'model_used': ['test'] * 20,
        'metadata': [json.dumps({'test': 1})] * 20
    })
    
    # Prepare dan train
    train_df = retrainer.prepare_training_data(test_feedback)
    result = retrainer.train_model(train_df, model_type='rf')
    
    print(f"Training result: {result}")
