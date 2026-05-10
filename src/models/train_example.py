"""
Training Model Example
======================
Contoh lengkap training model ML dengan berbagai algoritma.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
import logging
from datetime import datetime

# ML Libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# Metrics
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix
)

import mlflow
import mlflow.sklearn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Trainer untuk berbagai model ML.
    
    Usage:
        trainer = ModelTrainer(experiment_name="churn_prediction")
        results = trainer.train_all(X_train, X_test, y_train, y_test)
    """
    
    def __init__(self, experiment_name="default_experiment", tracking_uri=None):
        self.experiment_name = experiment_name
        self.models = {}
        self.results = {}
        
        # Setup MLflow
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        
        # Define models
        self.model_configs = {
            'logistic_regression': {
                'model': LogisticRegression(max_iter=1000, random_state=42),
                'params': {'C': [0.1, 1, 10]}
            },
            'random_forest': {
                'model': RandomForestClassifier(n_estimators=100, random_state=42),
                'params': {'n_estimators': [50, 100, 200]}
            },
            'gradient_boosting': {
                'model': GradientBoostingClassifier(n_estimators=100, random_state=42),
                'params': {'n_estimators': [50, 100]}
            },
            'xgboost': {
                'model': XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss'),
                'params': {'n_estimators': [50, 100, 200], 'max_depth': [3, 5, 7]}
            },
            'lightgbm': {
                'model': LGBMClassifier(n_estimators=100, random_state=42, verbose=-1),
                'params': {'n_estimators': [50, 100, 200], 'num_leaves': [31, 50]}
            },
            'svm': {
                'model': SVC(probability=True, random_state=42),
                'params': {'C': [0.1, 1, 10], 'kernel': ['rbf', 'linear']}
            }
        }
    
    def train_model(self, model_name, model, X_train, X_test, y_train, y_test):
        """Train single model dan log ke MLflow"""
        logger.info(f"Training {model_name}...")
        
        with mlflow.start_run(run_name=model_name):
            # Train
            model.fit(X_train, y_train)
            
            # Predict
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1_score': f1_score(y_test, y_pred, average='weighted'),
            }
            
            if y_pred_proba is not None:
                metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba)
            
            # Log ke MLflow
            mlflow.log_params(model.get_params())
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, model_name)
            
            # Store results
            self.models[model_name] = model
            self.results[model_name] = {
                'metrics': metrics,
                'predictions': y_pred,
                'probabilities': y_pred_proba
            }
            
            logger.info(f"{model_name} - Accuracy: {metrics['accuracy']:.4f}")
            
            return metrics
    
    def train_all(self, X_train, X_test, y_train, y_test):
        """Train semua model"""
        logger.info("="*50)
        logger.info("STARTING MODEL TRAINING")
        logger.info("="*50)
        
        for model_name, config in self.model_configs.items():
            try:
                self.train_model(
                    model_name,
                    config['model'],
                    X_train, X_test, y_train, y_test
                )
            except Exception as e:
                logger.error(f"Error training {model_name}: {e}")
        
        logger.info("="*50)
        logger.info("TRAINING COMPLETED")
        logger.info("="*50)
        
        return self.results
    
    def get_best_model(self, metric='f1_score'):
        """Get model dengan performa terbaik"""
        best_score = -1
        best_model = None
        best_name = None
        
        for name, result in self.results.items():
            score = result['metrics'].get(metric, 0)
            if score > best_score:
                best_score = score
                best_model = self.models[name]
                best_name = name
        
        logger.info(f"Best model: {best_name} ({metric}={best_score:.4f})")
        return best_name, best_model, best_score
    
    def save_best_model(self, output_dir='models/'):
        """Save model terbaik"""
        name, model, score = self.get_best_model()
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model_file = output_path / f'best_model_{name}.pkl'
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        
        # Save metadata
        metadata = {
            'model_name': name,
            'score': score,
            'created_at': datetime.now().isoformat(),
            'all_results': {k: v['metrics'] for k, v in self.results.items()}
        }
        
        with open(output_path / 'model_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Best model saved to {model_file}")
        return model_file
    
    def print_comparison(self):
        """Print comparison table semua model"""
        print("\n" + "="*80)
        print("MODEL COMPARISON")
        print("="*80)
        print(f"{'Model':<20} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1-Score':>10}")
        print("-"*80)
        
        for name, result in sorted(
            self.results.items(), 
            key=lambda x: x[1]['metrics']['f1_score'], 
            reverse=True
        ):
            m = result['metrics']
            print(f"{name:<20} {m['accuracy']:>10.4f} {m['precision']:>10.4f} {m['recall']:>10.4f} {m['f1_score']:>10.4f}")
        
        print("="*80)


def quick_train(X_train, X_test, y_train, y_test, model_type='xgboost'):
    """
    Quick training untuk satu model saja.
    
    Usage:
        model = quick_train(X_train, X_test, y_train, y_test, 'random_forest')
    """
    models = {
        'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'xgboost': XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss'),
        'lightgbm': LGBMClassifier(n_estimators=100, random_state=42, verbose=-1),
        'logistic': LogisticRegression(max_iter=1000, random_state=42)
    }
    
    if model_type not in models:
        raise ValueError(f"Model type {model_type} not available. Choose from {list(models.keys())}")
    
    model = models[model_type]
    logger.info(f"Training {model_type}...")
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"Accuracy: {accuracy:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return model


if __name__ == "__main__":
    # Load processed data
    try:
        X_train = pd.read_csv('data/processed/X_train.csv')
        X_test = pd.read_csv('data/processed/X_test.csv')
        y_train = pd.read_csv('data/processed/y_train.csv').values.ravel()
        y_test = pd.read_csv('data/processed/y_test.csv').values.ravel()
        
        print(f"Loaded data: Train={X_train.shape}, Test={X_test.shape}")
        
    except FileNotFoundError:
        print("❌ Processed data not found!")
        print("Please run: python src/data/pipeline.py")
        exit(1)
    
    # Option 1: Train all models
    print("\n🚀 Training all models...")
    trainer = ModelTrainer(experiment_name="customer_churn")
    results = trainer.train_all(X_train, X_test, y_train, y_test)
    trainer.print_comparison()
    trainer.save_best_model()
    
    # Option 2: Quick train single model
    # print("\n🚀 Quick training XGBoost...")
    # model = quick_train(X_train, X_test, y_train, y_test, 'xgboost')
