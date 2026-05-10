#!/usr/bin/env python
"""
Real Predictor - Menggunakan model dan data yang sudah ada
Prediksi REAL dengan data customer churn, fraud, sales, credit scoring
"""

import os
import json
import pickle
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

logger = logging.getLogger(__name__)


class RealPredictor:
    """
    Predictor yang menggunakan model dan data REAL
    Datasets: customer_churn, fraud_detection, sales_forecast, credit_scoring
    """
    
    def __init__(self, models_dir: str = "models", data_dir: str = "data"):
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        
        # Load semua model yang tersedia
        self.models = {}
        self.model_info = {}
        self.datasets = {}
        self.scalers = {}
        
        self._load_all_models()
        self._load_datasets()
        
        logger.info(f"[OK] RealPredictor loaded: {len(self.models)} models, {len(self.datasets)} datasets")
    
    def _load_all_models(self):
        """Load semua model .pkl yang tersedia"""
        if not self.models_dir.exists():
            return
        
        for pkl_file in self.models_dir.glob("*.pkl"):
            try:
                with open(pkl_file, 'rb') as f:
                    model = pickle.load(f)
                
                model_id = pkl_file.stem
                self.models[model_id] = model
                
                # Try to load metadata
                meta_file = pkl_file.with_suffix('.json')
                if meta_file.exists():
                    with open(meta_file) as f:
                        self.model_info[model_id] = json.load(f)
                else:
                    self.model_info[model_id] = {'type': 'unknown', 'file': str(pkl_file)}
                
                logger.info(f"[OK] Loaded model: {model_id}")
                
            except Exception as e:
                logger.warning(f"[WARN] Failed to load {pkl_file}: {e}")
    
    def _load_datasets(self):
        """Load datasets real untuk referensi dan preprocessing"""
        datasets = {
            'customer_churn': 'raw/customer_churn_data.csv',
            'fraud_detection': 'raw/fraud_detection_data.csv',
            'sales_forecast': 'raw/sales_data.csv',
            'credit_scoring': 'raw/credit_scoring_data.csv'
        }
        
        for name, path in datasets.items():
            full_path = self.data_dir / path
            if full_path.exists():
                try:
                    df = pd.read_csv(full_path)
                    self.datasets[name] = df
                    
                    # Fit scaler untuk dataset ini
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        scaler = StandardScaler()
                        scaler.fit(df[numeric_cols].fillna(0))
                        self.scalers[name] = scaler
                    
                    logger.info(f"[OK] Loaded dataset: {name} ({len(df)} rows)")
                except Exception as e:
                    logger.warning(f"[WARN] Failed to load {name}: {e}")
    
    def get_available_models(self) -> List[str]:
        """List semua model yang tersedia"""
        return list(self.models.keys())
    
    def get_available_datasets(self) -> List[str]:
        """List semua dataset yang tersedia"""
        return list(self.datasets.keys())
    
    def predict(self, model_id: str, input_data: Dict) -> Dict:
        """
        Prediksi REAL dengan model yang sudah dilatih
        
        Args:
            model_id: ID model (e.g., 'best_model_logistic_regression')
            input_data: Dictionary dengan feature values
        
        Returns:
            Dictionary dengan hasil prediksi dan confidence
        """
        if model_id not in self.models:
            return {
                'error': f'Model {model_id} not found',
                'available': self.get_available_models()
            }
        
        model = self.models[model_id]
        
        try:
            # Convert input ke DataFrame
            df_input = pd.DataFrame([input_data])
            
            # Preprocessing (basic)
            df_input = df_input.fillna(0)
            
            # Prediksi
            prediction = model.predict(df_input)[0]
            
            # Confidence (jika model support predict_proba)
            confidence = 0.5
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(df_input)[0]
                confidence = float(np.max(proba))
            
            # Feature importance (jika available)
            feature_importance = None
            if hasattr(model, 'feature_importances_'):
                feature_importance = dict(zip(df_input.columns, model.feature_importances_))
            elif hasattr(model, 'coef_'):
                feature_importance = dict(zip(df_input.columns, np.abs(model.coef_[0])))
            
            return {
                'prediction': int(prediction),
                'prediction_label': 'Positive' if prediction == 1 else 'Negative',
                'confidence': confidence,
                'confidence_pct': f"{confidence*100:.1f}%",
                'model_used': model_id,
                'input_features': list(input_data.keys()),
                'feature_importance': feature_importance,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Prediction failed: {e}")
            return {
                'error': str(e),
                'model_used': model_id
            }
    
    def predict_batch(self, model_id: str, inputs: List[Dict]) -> List[Dict]:
        """Batch prediction untuk multiple inputs"""
        results = []
        for inp in inputs:
            result = self.predict(model_id, inp)
            results.append(result)
        return results
    
    def generate_synthetic_feedback(self, prediction: Dict, true_label: Optional[int] = None) -> int:
        """
        Generate feedback berdasarkan confidence dan prediction
        Untuk demo: feedback positif jika confidence > 0.7
        """
        if true_label is not None:
            # Jika ada ground truth, bandingkan
            return 1 if prediction['prediction'] == true_label else 0
        else:
            # Simulasi feedback berdasarkan confidence
            confidence = prediction['confidence']
            # Higher confidence = higher chance positive feedback
            prob_positive = 0.3 + (confidence * 0.6)  # 0.3 to 0.9
            return 1 if np.random.random() < prob_positive else 0
    
    def get_sample_input(self, dataset_name: str = 'customer_churn') -> Dict:
        """Get sample input dari dataset real"""
        if dataset_name not in self.datasets:
            return {'error': f'Dataset {dataset_name} not found'}
        
        df = self.datasets[dataset_name]
        
        # Ambil random row
        sample = df.sample(1).iloc[0].to_dict()
        
        # Remove target column jika ada
        target_cols = ['churn', 'is_fraud', 'sales', 'risk_score', 'target', 'label']
        for col in target_cols:
            if col in sample:
                del sample[col]
        
        return sample
    
    def get_model_performance(self, model_id: str) -> Dict:
        """Get performance metrics untuk model"""
        if model_id not in self.model_info:
            return {'error': 'Model info not found'}
        
        info = self.model_info[model_id]
        
        # Query database untuk actual performance
        try:
            conn = sqlite3.connect("logs/feedback/self_improve.db")
            
            # Get feedback untuk model ini
            cursor = conn.execute(
                """SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN user_feedback = 1 THEN 1 ELSE 0 END) as positive,
                    AVG(confidence) as avg_confidence
                FROM interactions 
                WHERE model_used = ?""",
                (model_id,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                'model_id': model_id,
                'model_info': info,
                'interactions': row[0] or 0,
                'positive_feedback': row[1] or 0,
                'avg_confidence': row[2] or 0,
                'satisfaction_rate': (row[1] / row[0] * 100) if row[0] > 0 else 0
            }
            
        except Exception as e:
            return {
                'model_id': model_id,
                'model_info': info,
                'error': str(e)
            }


if __name__ == '__main__':
    # Test RealPredictor
    logging.basicConfig(level=logging.INFO)
    
    predictor = RealPredictor()
    
    print("\n" + "="*60)
    print("REAL PREDICTOR TEST")
    print("="*60)
    
    print(f"\nAvailable Models: {predictor.get_available_models()}")
    print(f"Available Datasets: {predictor.get_available_datasets()}")
    
    # Test prediction dengan sample input
    if predictor.get_available_models():
        model_id = predictor.get_available_models()[0]
        
        # Get sample input
        sample = predictor.get_sample_input('customer_churn')
        print(f"\nSample Input: {sample}")
        
        # Predict
        result = predictor.predict(model_id, sample)
        print(f"\nPrediction Result:")
        print(json.dumps(result, indent=2, default=str))
