#!/usr/bin/env python
"""
Evaluator - Sistem evaluasi otomatis dan drift detection
Mendeteksi perubahan data dan penurunan performa model
"""

import json
import logging
import pickle
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
import sqlite3

import numpy as np
import pandas as pd
from scipy import stats

# Optional imports dengan fallback
try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset, ClassificationPreset
    EVIDENTLY_AVAILABLE = True
except Exception as e:
    EVIDENTLY_AVAILABLE = False
    logging.warning(f"Evidently not available: {e}")

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)


class Evaluator:
    """
    Sistem evaluasi untuk mendeteksi drift dan menilai performa model
    """
    
    def __init__(
        self,
        reference_data_path: str,
        db_path: str = "logs/feedback/self_improve.db",
        drift_threshold: float = 0.05
    ):
        """
        Initialize Evaluator
        
        Args:
            reference_data_path: Path ke reference dataset (baseline)
            db_path: Path ke SQLite database
            drift_threshold: Threshold untuk drift detection (p-value)
        """
        self.reference_data = pd.read_csv(reference_data_path)
        self.drift_threshold = drift_threshold
        self.db_path = db_path
        
        # Extract feature columns (exclude target)
        self.feature_cols = [c for c in self.reference_data.columns 
                           if c not in ['target', 'label', 'y', 'class']]
        
        logger.info(f"[OK] Evaluator initialized with {len(self.feature_cols)} features")
    
    def detect_drift_basic(
        self,
        current_data: pd.DataFrame,
        method: str = "ks"
    ) -> Dict[str, Any]:
        """
        Deteksi drift dengan statistical tests (tanpa Evidently)
        
        Args:
            current_data: DataFrame dengan data terbaru
            method: 'ks' (Kolmogorov-Smirnov) atau 'psi' (Population Stability Index)
        
        Returns:
            Dictionary dengan drift scores per feature
        """
        drift_results = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'features': {},
            'drift_detected': False,
            'drifted_features': []
        }
        
        for col in self.feature_cols:
            if col not in current_data.columns:
                continue
                
            ref_values = self.reference_data[col].dropna()
            cur_values = current_data[col].dropna()
            
            if len(ref_values) == 0 or len(cur_values) == 0:
                continue
            
            if method == "ks":
                # Kolmogorov-Smirnov test untuk numerical
                if ref_values.dtype in ['int64', 'float64']:
                    statistic, p_value = stats.ks_2samp(ref_values, cur_values)
                    drifted = p_value < self.drift_threshold
                    
                    drift_results['features'][col] = {
                        'p_value': float(p_value),
                        'statistic': float(statistic),
                        'drifted': drifted
                    }
                    
                    if drifted:
                        drift_results['drift_detected'] = True
                        drift_results['drifted_features'].append(col)
            
            elif method == "psi":
                # Population Stability Index
                psi_score = self._calculate_psi(ref_values, cur_values)
                drifted = psi_score > 0.25  # PSI > 0.25 considered significant
                
                drift_results['features'][col] = {
                    'psi': float(psi_score),
                    'drifted': drifted
                }
                
                if drifted:
                    drift_results['drift_detected'] = True
                    drift_results['drifted_features'].append(col)
        
        # Log ke database
        self._log_drift(drift_results)
        
        return drift_results
    
    def _calculate_psi(self, expected: pd.Series, actual: pd.Series, bins: int = 10) -> float:
        """Calculate Population Stability Index"""
        # Binning
        breakpoints = np.linspace(expected.min(), expected.max(), bins + 1)
        
        expected_counts, _ = np.histogram(expected, breakpoints)
        actual_counts, _ = np.histogram(actual, breakpoints)
        
        # Convert to percentages
        expected_percents = expected_counts / len(expected)
        actual_percents = actual_counts / len(actual)
        
        # Handle zero divisions
        expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
        actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)
        
        # Calculate PSI
        psi = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))
        
        return psi
    
    def detect_drift_evidently(self, current_data_path: str) -> Dict:
        """
        Deteksi drift menggunakan Evidently (lebih komprehensif)
        
        Requires: pip install evidently
        """
        if not EVIDENTLY_AVAILABLE:
            logger.error("Evidently not installed. Use detect_drift_basic instead.")
            return {'error': 'evidently_not_available'}
        
        current_df = pd.read_csv(current_data_path)
        
        report = Report(metrics=[DataDriftPreset()])
        report.run(
            reference_data=self.reference_data,
            current_data=current_df
        )
        
        result = report.as_dict()
        
        drift_results = {
            'timestamp': datetime.now().isoformat(),
            'method': 'evidently',
            'dataset_drift': result['metrics'][0]['result']['dataset_drift'],
            'drift_share': result['metrics'][0]['result']['drift_share'],
            'number_of_drifted_columns': result['metrics'][0]['result']['number_of_drifted_columns'],
            'details': result
        }
        
        self._log_drift(drift_results)
        
        return drift_results
    
    def _log_drift(self, drift_results: Dict):
        """Log drift detection ke database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if drift_results.get('features'):
                for feature, data in drift_results['features'].items():
                    conn.execute(
                        """INSERT INTO drift_history 
                           (timestamp, feature_name, drift_score, drift_detected, threshold)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            drift_results['timestamp'],
                            feature,
                            data.get('p_value', data.get('psi', 0)),
                            data.get('drifted', False),
                            self.drift_threshold
                        )
                    )
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log drift: {e}")
    
    def evaluate_model(
        self,
        model_path: str,
        test_data_path: str,
        model_id: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Evaluasi performa model pada test set
        
        Args:
            model_path: Path ke model pickle
            test_data_path: Path ke test data CSV
            model_id: Identifier untuk model
        
        Returns:
            Dictionary dengan metrics
        """
        # Load model
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Load test data
        test_df = pd.read_csv(test_data_path)
        
        # Identify target column
        target_col = None
        for col in ['target', 'label', 'y', 'class']:
            if col in test_df.columns:
                target_col = col
                break
        
        if not target_col:
            raise ValueError("No target column found in test data")
        
        X_test = test_df.drop(columns=[target_col])
        y_test = test_df[target_col]
        
        # Predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            roc_auc_score, mean_squared_error, r2_score
        )
        
        metrics = {}
        
        # Classification metrics
        try:
            metrics['accuracy'] = accuracy_score(y_test, y_pred)
            metrics['precision'] = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            metrics['recall'] = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            metrics['f1_score'] = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            # ROC-AUC (binary/multiclass)
            if hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(X_test)
                if y_proba.shape[1] == 2:
                    metrics['roc_auc'] = roc_auc_score(y_test, y_proba[:, 1])
                else:
                    metrics['roc_auc'] = roc_auc_score(y_test, y_proba, multi_class='ovr')
        except Exception as e:
            logger.warning(f"Classification metrics failed: {e}")
        
        # Log ke MLflow jika tersedia
        if MLFLOW_AVAILABLE and model_id:
            with mlflow.start_run(run_name=f"eval_{model_id}"):
                mlflow.log_params({
                    'model_path': model_path,
                    'test_data': test_data_path
                })
                for name, value in metrics.items():
                    mlflow.log_metric(name, value)
        
        logger.info(f"[OK] Model evaluation: {metrics}")
        return metrics
    
    def compare_models(
        self,
        model_paths: List[str],
        test_data_path: str,
        metric: str = 'f1_score'
    ) -> Tuple[str, Dict]:
        """
        Bandingkan beberapa model dan pilih yang terbaik
        
        Returns:
            (best_model_path, all_metrics)
        """
        results = {}
        
        for model_path in model_paths:
            model_id = Path(model_path).stem
            metrics = self.evaluate_model(model_path, test_data_path, model_id)
            results[model_path] = metrics
        
        # Find best model
        best_model = max(results.keys(), key=lambda x: results[x].get(metric, 0))
        
        logger.info(f"[OK] Best model: {Path(best_model).name} ({metric}={results[best_model].get(metric):.4f})")
        
        return best_model, results
    
    def should_retrain(
        self,
        current_metrics: Dict[str, float],
        baseline_metrics: Dict[str, float],
        threshold_drop: float = 0.05
    ) -> Tuple[bool, str]:
        """
        Tentukan apakah perlu retraining berdasarkan perbandingan metrics
        
        Returns:
            (should_retrain, reason)
        """
        for metric, baseline in baseline_metrics.items():
            if metric in current_metrics:
                current = current_metrics[metric]
                drop = baseline - current
                
                if drop > threshold_drop:
                    reason = f"{metric} dropped by {drop:.4f} (baseline: {baseline:.4f}, current: {current:.4f})"
                    logger.warning(f"[ALERT] {reason}")
                    return True, reason
        
        return False, "Performance within acceptable range"


if __name__ == '__main__':
    # Test Evaluator
    logging.basicConfig(level=logging.INFO)
    
    # Buat test data
    import numpy as np
    
    np.random.seed(42)
    n_samples = 1000
    
    ref_data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, n_samples),
        'feature2': np.random.normal(5, 2, n_samples),
        'feature3': np.random.choice(['A', 'B', 'C'], n_samples),
        'target': np.random.choice([0, 1], n_samples)
    })
    ref_data.to_csv('data/processed/reference_test.csv', index=False)
    
    # Current data dengan drift
    cur_data = pd.DataFrame({
        'feature1': np.random.normal(2, 1.5, n_samples),  # Drift!
        'feature2': np.random.normal(5, 2, n_samples),
        'feature3': np.random.choice(['A', 'B', 'C'], n_samples),
        'target': np.random.choice([0, 1], n_samples)
    })
    cur_data.to_csv('data/processed/current_test.csv', index=False)
    
    # Test drift detection
    evaluator = Evaluator('data/processed/reference_test.csv')
    
    drift = evaluator.detect_drift_basic(cur_data, method='ks')
    print(f"Drift detected: {drift['drift_detected']}")
    print(f"Drifted features: {drift['drifted_features']}")
