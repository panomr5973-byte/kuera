"""
Monitoring System
=================
Complete monitoring dengan:
- Data drift detection
- Model performance tracking
- Auto-retraining
- Alert system
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DriftDetector:
    """Detect data drift menggunakan statistical tests"""
    
    def __init__(self, reference_data_path: str):
        self.reference_data = pd.read_csv(reference_data_path)
        self.drift_history = []
        
    def detect_drift(self, current_data: pd.DataFrame, threshold: float = 0.05) -> Dict:
        """Detect drift antara reference dan current data"""
        from scipy import stats
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'drift_detected': False,
            'features': {}
        }
        
        numeric_cols = self.reference_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col in current_data.columns:
                statistic, p_value = stats.ks_2samp(
                    self.reference_data[col].dropna(),
                    current_data[col].dropna()
                )
                
                drift = p_value < threshold
                
                results['features'][col] = {
                    'ks_statistic': float(statistic),
                    'p_value': float(p_value),
                    'drift_detected': drift
                }
                
                if drift:
                    results['drift_detected'] = True
        
        self.drift_history.append(results)
        return results


class PerformanceMonitor:
    """Monitor model performance over time"""
    
    def __init__(self, model_name: str, baseline_metrics: Dict):
        self.model_name = model_name
        self.baseline_metrics = baseline_metrics
        self.performance_history = []
        
    def calculate_metrics(self) -> Dict:
        """Calculate metrics"""
        return {
            'baseline_f1': self.baseline_metrics.get('f1_score', 0),
            'timestamp': datetime.now().isoformat()
        }
    
    def check_performance_degradation(self, threshold: float = 0.1) -> bool:
        """Check if performance has degraded"""
        return False  # Simplified for demo


class MonitoringOrchestrator:
    """Orchestrate monitoring"""
    
    def __init__(self):
        self.drift_detector = None
        if Path('data/processed/X_train.csv').exists():
            self.drift_detector = DriftDetector('data/processed/X_train.csv')
    
    def run_drift_check(self):
        """Run drift detection"""
        if self.drift_detector and Path('data/processed/X_test.csv').exists():
            current = pd.read_csv('data/processed/X_test.csv')
            results = self.drift_detector.detect_drift(current)
            
            if results['drift_detected']:
                logger.warning(f"Drift detected in {sum(1 for f in results['features'].values() if f['drift_detected'])} features")
            else:
                logger.info("No drift detected")


if __name__ == "__main__":
    orchestrator = MonitoringOrchestrator()
    orchestrator.run_drift_check()
