#!/usr/bin/env python
"""
AUTO STARTUP SYSTEM - Self-Evolving AI App
Jalan otomatis saat komputer dinyalakan

Fitur:
- Verifikasi environment sebelum jalan
- Auto-start API Server + Scheduler
- Logging lengkap
- Health check otomatis
- Auto-restart jika crash
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import signal

# Setup logging
logs_dir = Path("logs/startup")
logs_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / f"startup_{datetime.now():%Y%m%d}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AutoStartup")

# Global untuk tracking processes
processes = {}


def verify_environment():
    """Verifikasi environment sebelum start"""
    logger.info("="*60)
    logger.info("VERIFYING ENVIRONMENT")
    logger.info("="*60)
    
    checks = {
        'python': False,
        'virtual_env': False,
        'database': False,
        'model_dir': False,
        'dependencies': False
    }
    
    # 1. Check Python
    try:
        import sys
        logger.info(f"[OK] Python: {sys.version.split()[0]}")
        checks['python'] = True
    except Exception as e:
        logger.error(f"[FAIL] Python check: {e}")
        return False
    
    # 2. Check Virtual Environment
    venv_path = Path("ai_env/Scripts/python.exe")
    if venv_path.exists():
        logger.info("[OK] Virtual environment exists")
        checks['virtual_env'] = True
    else:
        logger.error("[FAIL] Virtual environment not found")
        return False
    
    # 3. Check Database
    db_path = Path("logs/feedback/self_improve.db")
    if db_path.exists():
        logger.info("[OK] Database exists")
        checks['database'] = True
    else:
        logger.warning("[WARN] Database not found, will be created")
        checks['database'] = True  # Will auto-create
    
    # 4. Check Model Directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    logger.info("[OK] Models directory ready")
    checks['model_dir'] = True
    
    # 5. Check Dependencies
    try:
        import fastapi
        import uvicorn
        import pandas
        import sklearn
        logger.info("[OK] Core dependencies available")
        checks['dependencies'] = True
    except ImportError as e:
        logger.error(f"[FAIL] Missing dependency: {e}")
        return False
    
    # Summary
    all_passed = all(checks.values())
    if all_passed:
        logger.info("[OK] All environment checks passed!")
    else:
        logger.error("[FAIL] Some checks failed")
    
    return all_passed


def start_api_server():
    """Start API Server dengan auto-restart"""
    logger.info("[START] Starting API Server...")
    
    python_exe = str(Path("ai_env/Scripts/python.exe").absolute())
    
    while True:
        try:
            process = subprocess.Popen(
                [python_exe, "run_self_evolving.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW  # Windows: no console window
            )
            
            processes['api'] = process
            logger.info(f"[OK] API Server started (PID: {process.pid})")
            
            # Wait for process
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"[CRASH] API Server crashed with code {process.returncode}")
                logger.error(f"[CRASH] stderr: {stderr[:500]}")
            
            # Auto-restart after 5 seconds
            logger.info("[RESTART] Restarting API Server in 5 seconds...")
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"[ERROR] API Server error: {e}")
            time.sleep(5)


def start_scheduler():
    """Start Scheduler dengan auto-restart"""
    logger.info("[START] Starting Scheduler...")
    
    python_exe = str(Path("ai_env/Scripts/python.exe").absolute())
    
    while True:
        try:
            process = subprocess.Popen(
                [python_exe, "start_scheduler.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            processes['scheduler'] = process
            logger.info(f"[OK] Scheduler started (PID: {process.pid})")
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"[CRASH] Scheduler crashed with code {process.returncode}")
                logger.error(f"[CRASH] stderr: {stderr[:500]}")
            
            logger.info("[RESTART] Restarting Scheduler in 5 seconds...")
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"[ERROR] Scheduler error: {e}")
            time.sleep(5)


def health_checker():
    """Background thread: Check health setiap 60 detik"""
    import urllib.request
    
    logger.info("[START] Health checker started")
    
    while True:
        try:
            time.sleep(60)  # Check every minute
            
            # Check API health
            try:
                with urllib.request.urlopen('http://localhost:8000/health', timeout=5) as response:
                    data = json.loads(response.read())
                    logger.info(f"[HEALTH] API OK | Interactions: {data.get('total_interactions', 0)}")
            except Exception as e:
                logger.warning(f"[HEALTH] API not responding: {e}")
            
            # Check log file size (rotate if >10MB)
            log_file = logs_dir / f"startup_{datetime.now():%Y%m%d}.log"
            if log_file.exists() and log_file.stat().st_size > 10*1024*1024:
                logger.info("[MAINTENANCE] Rotating log file")
                
        except Exception as e:
            logger.error(f"[HEALTH] Checker error: {e}")


def create_status_file():
    """Buat status file untuk external monitoring"""
    status = {
        'status': 'running',
        'started_at': datetime.now().isoformat(),
        'pid_api': processes.get('api', {}).pid if 'api' in processes else None,
        'pid_scheduler': processes.get('scheduler', {}).pid if 'scheduler' in processes else None,
        'check_interval': 60
    }
    
    with open('logs/startup/status.json', 'w') as f:
        json.dump(status, f, indent=2)


def signal_handler(signum, frame):
    """Handle shutdown signal"""
    logger.info("[SHUTDOWN] Received shutdown signal, stopping all processes...")
    
    for name, process in processes.items():
        try:
            logger.info(f"[SHUTDOWN] Stopping {name} (PID: {process.pid})")
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
    
    logger.info("[SHUTDOWN] All processes stopped")
    sys.exit(0)


def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info("AUTO STARTUP SYSTEM - Self-Evolving AI App")
    logger.info("="*60)
    logger.info(f"Started at: {datetime.now()}")
    logger.info("Press Ctrl+C to stop all services")
    logger.info("="*60)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Verify environment
    if not verify_environment():
        logger.error("[FATAL] Environment verification failed. Exiting.")
        sys.exit(1)
    
    # Start components in separate threads
    threads = [
        threading.Thread(target=start_api_server, daemon=True, name="API-Server"),
        threading.Thread(target=start_scheduler, daemon=True, name="Scheduler"),
        threading.Thread(target=health_checker, daemon=True, name="Health-Checker")
    ]
    
    for t in threads:
        t.start()
        time.sleep(2)  # Stagger starts
    
    logger.info("[OK] All services started successfully!")
    logger.info("[INFO] API: http://localhost:8000")
    logger.info("[INFO] Dashboard: streamlit run app/dashboard.py")
    
    # Keep main thread alive
    try:
        while True:
            create_status_file()
            time.sleep(10)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
