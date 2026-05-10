#!/usr/bin/env python
"""
Start Auto-Retrain Scheduler (Windows compatible)
Jalankan di background untuk retraining otomatis
"""
import sys
import logging
from self_evolving.retrainer import AutoRetrain, RetrainConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/feedback/scheduler.log')
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print("="*60)
    print("AUTO-RETRAIN SCHEDULER")
    print("="*60)
    print("Check interval: Every 1 hour")
    print("Min samples: 50")
    print("Log file: logs/feedback/scheduler.log")
    print("="*60)
    
    config = RetrainConfig(
        min_samples=50,
        check_interval_hours=1,
        performance_threshold=0.05
    )
    
    retrainer = AutoRetrain(config=config)
    
    try:
        retrainer.schedule_retrain()
    except KeyboardInterrupt:
        print("\n[OK] Scheduler stopped")
