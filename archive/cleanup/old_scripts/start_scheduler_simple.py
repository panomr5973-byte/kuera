#!/usr/bin/env python
"""
Simple Scheduler - Tanpa dependency Evidently
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/feedback/scheduler.log')
    ]
)

logger = logging.getLogger(__name__)

def run_scheduler():
    """Run scheduler dengan retrainer sederhana"""
    logger.info("="*60)
    logger.info("SIMPLE SCHEDULER - Auto-Retrain")
    logger.info("="*60)
    
    try:
        # Import hanya yang diperlukan
        sys.path.insert(0, str(Path(__file__).parent))
        from self_evolving.data_collector import DataCollector
        from self_evolving.retrainer import RetrainConfig
        
        # Cek data
        collector = DataCollector()
        stats = collector.get_feedback_stats(hours=24*7)
        total = stats.get('total_feedback', 0)
        
        logger.info(f"Total feedback: {total}")
        
        if total >= 50:
            logger.info("[TRIGGER] Threshold reached! Starting retrain...")
            
            # Import retrainer
            from self_evolving.retrainer import AutoRetrain
            
            config = RetrainConfig(min_samples=50, check_interval_hours=24)
            retrainer = AutoRetrain(config=config)
            
            # Trigger retrain
            result = retrainer.check_and_trigger_retrain(force=True)
            
            if result:
                logger.info(f"[OK] Retrain success: {result.get('model_id')}")
                logger.info(f"[OK] Metrics: {result.get('metrics')}")
            else:
                logger.info("[SKIP] Retrain not triggered")
        else:
            logger.info(f"[SKIP] Need 50+ feedback, have {total}")
        
        collector.close()
        
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    run_scheduler()
    print("\n[OK] Scheduler completed! Check logs/feedback/scheduler.log")
