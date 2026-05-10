#!/usr/bin/env python3
"""
Pipeline Runner
===============
Script untuk menjalankan pipeline end-to-end dengan satu command.

Usage:
    python run_pipeline.py --step all
    python run_pipeline.py --step data
    python run_pipeline.py --step train
    python run_pipeline.py --step dashboard
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_data_pipeline():
    """Run data processing pipeline"""
    print("\n" + "="*60)
    print("STEP 1: DATA PROCESSING PIPELINE")
    print("="*60)
    
    from src.data.pipeline import create_sample_data, DataPipeline
    
    # Create sample data
    create_sample_data()
    
    # Run pipeline
    pipeline = DataPipeline()
    pipeline.config['target_column'] = 'target'
    pipeline.config['categorical_columns'] = ['gender', 'city']
    pipeline.config['drop_columns'] = ['customer_id']
    
    X_train, X_test, y_train, y_test = pipeline.run(
        'data/raw/sample_dataset.csv',
        'data/processed/'
    )
    
    print("\n✅ Data pipeline completed!")
    print(f"   Train set: {X_train.shape}")
    print(f"   Test set: {X_test.shape}")
    return True


def run_training():
    """Run model training"""
    print("\n" + "="*60)
    print("STEP 2: MODEL TRAINING")
    print("="*60)
    
    import pandas as pd
    from src.models.train_example import ModelTrainer
    
    # Load data
    try:
        X_train = pd.read_csv('data/processed/X_train.csv')
        X_test = pd.read_csv('data/processed/X_test.csv')
        y_train = pd.read_csv('data/processed/y_train.csv').values.ravel()
        y_test = pd.read_csv('data/processed/y_test.csv').values.ravel()
    except FileNotFoundError:
        print("❌ Processed data not found! Run data pipeline first.")
        return False
    
    # Train models
    trainer = ModelTrainer(experiment_name="customer_churn")
    results = trainer.train_all(X_train, X_test, y_train, y_test)
    trainer.print_comparison()
    trainer.save_best_model()
    
    print("\n✅ Model training completed!")
    return True


def run_dashboard():
    """Launch Streamlit dashboard"""
    print("\n" + "="*60)
    print("STEP 3: LAUNCHING DASHBOARD")
    print("="*60)
    
    print("\n🚀 Starting Streamlit dashboard...")
    print("   URL: http://localhost:8501")
    print("   Press Ctrl+C to stop\n")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "app/dashboard.py",
        "--server.port", "8501"
    ])
    return True


def main():
    parser = argparse.ArgumentParser(description='AI Project Pipeline Runner')
    parser.add_argument(
        '--step',
        choices=['all', 'data', 'train', 'dashboard'],
        default='all',
        help='Which step to run'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🤖 AI PROJECT PIPELINE RUNNER")
    print("="*60)
    
    if args.step in ['all', 'data']:
        if not run_data_pipeline():
            sys.exit(1)
    
    if args.step in ['all', 'train']:
        if not run_training():
            sys.exit(1)
    
    if args.step in ['all', 'dashboard']:
        run_dashboard()
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETED!")
    print("="*60)


if __name__ == "__main__":
    main()
