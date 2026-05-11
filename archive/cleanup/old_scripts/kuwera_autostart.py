#!/usr/bin/env python
"""
KUWERA AI - Advanced Auto-Startup System
Integrates 12 models with Web Interface and Evolution Tracking

Fitur:
- Auto-start Web Server (Flask)
- Auto-start Model Management
- Health monitoring untuk 12 model
- Evolution tracking
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
logs_dir = Path("logs/kuwera")
logs_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / f"kuwera_{datetime.now():%Y%m%d}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("KUWERA-AutoStart")

# Global process tracking
processes = {}
services_status = {}

# Service configurations
SERVICES = {
    'web_server': {
        'name': 'KUWERA Web Server',
        'script': 'kuwera_web_server.py',
        'port': 5000,
        'url': 'http://localhost:5000',
        'required': True
    },
    'api_server': {
        'name': 'KUWERA API',
        'script': 'run_self_evolving.py',
        'port': 8000,
        'url': 'http://localhost:8000',
        'required': False
    },
    'scheduler': {
        'name': 'Evolution Scheduler',
        'script': 'start_scheduler.py',
        'port': None,
        'url': None,
        'required': False
    }
}


def verify_kuwera_environment():
    """Verifikasi environment KUWERA yang lengkap"""
    logger.info("="*70)
    logger.info("KUWERA AI - ENVIRONMENT VERIFICATION")
    logger.info("="*70)
    
    checks = {
        'python': False,
        'virtual_env': False,
        'models_dir': False,
        'model_registry': False,
        'dependencies': False,
        'databases': False
    }
    
    # 1. Check Python
    try:
        version = sys.version.split()[0]
        logger.info(f"[OK] Python {version}")
        checks['python'] = True
    except Exception as e:
        logger.error(f"[FAIL] Python: {e}")
        return False
    
    # 2. Check Virtual Environment
    venv_python = Path("ai_env/Scripts/python.exe")
    if venv_python.exists():
        logger.info("[OK] Virtual environment: ai_env")
        checks['virtual_env'] = True
    else:
        logger.error("[FAIL] Virtual environment not found")
        return False
    
    # 3. Check Model Directory
    models_dir = Path("models/llm")
    if models_dir.exists():
        gguf_files = list(models_dir.glob("*.gguf"))
        total_size = sum(f.stat().st_size for f in gguf_files) / (1024**3)
        logger.info(f"[OK] Models directory: {len(gguf_files)} models, {total_size:.2f} GB")
        checks['models_dir'] = True
    else:
        logger.warning("[WARN] Models directory not found")
    
    # 4. Check Model Registry
    registry_file = models_dir / "model_registry_active.json"
    if registry_file.exists():
        with open(registry_file) as f:
            registry = json.load(f)
        logger.info(f"[OK] Model registry: {registry.get('total_models', 0)} models")
        checks['model_registry'] = True
        
        # Log model categories
        categories = {
            'Indonesian': len(registry.get('indonesian_models', [])),
            'Multilingual': len(registry.get('multilingual_models', [])),
            'Coding': len(registry.get('coding_models', [])),
            'Bartowski': len(registry.get('bartowski_models', [])),
            'Long Context': len(registry.get('long_context_models', []))
        }
        logger.info(f"      Categories: {categories}")
    else:
        logger.warning("[WARN] Model registry not found")
    
    # 5. Check Dependencies
    try:
        import flask
        import flask_cors
        logger.info("[OK] Core web dependencies")
        
        # Check optional dependencies
        try:
            import ctransformers
            logger.info("[OK] CTransformers available")
        except:
            logger.warning("[WARN] CTransformers not installed")
        
        try:
            import websockets
            logger.info("[OK] WebSocket available")
        except:
            logger.warning("[WARN] WebSocket not installed")
            
        checks['dependencies'] = True
    except ImportError as e:
        logger.error(f"[FAIL] Missing dependency: {e}")
        return False
    
    # 6. Check Databases
    data_dir = Path("data")
    databases = {
        'kuera_evolution.db': 'Evolution tracking',
        'worldbank_indonesia.db': 'World Bank data',
        'international_data.db': 'International data'
    }
    
    db_ok = True
    for db_file, desc in databases.items():
        db_path = data_dir / db_file
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024**2)
            logger.info(f"[OK] {desc}: {size_mb:.1f} MB")
        else:
            logger.warning(f"[WARN] {desc} not found (will be created)")
    
    checks['databases'] = True
    
    # Summary
    all_passed = all(checks.values())
    if all_passed:
        logger.info("[OK] All environment checks passed!")
    else:
        logger.warning("[WARN] Some checks failed, but continuing...")
    
    logger.info("="*70)
    return True


def start_service(service_id, config):
    """Start a service with auto-restart"""
    logger.info(f"[START] {config['name']}...")
    
    python_exe = str(Path("ai_env/Scripts/python.exe").absolute())
    script_path = Path(config['script'])
    
    if not script_path.exists():
        logger.error(f"[FAIL] Script not found: {config['script']}")
        return
    
    restart_count = 0
    max_restarts = 10
    
    while restart_count < max_restarts:
        try:
            process = subprocess.Popen(
                [python_exe, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            processes[service_id] = process
            services_status[service_id] = {
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'pid': process.pid,
                'restarts': restart_count
            }
            
            logger.info(f"[OK] {config['name']} started (PID: {process.pid})")
            
            # Wait for process
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                restart_count += 1
                logger.error(f"[CRASH] {config['name']} crashed (code: {process.returncode})")
                if stderr:
                    logger.error(f"[CRASH] Error: {stderr[:500]}")
                
                if restart_count < max_restarts:
                    logger.info(f"[RESTART] Restarting {config['name']} in 5 seconds... (attempt {restart_count}/{max_restarts})")
                    time.sleep(5)
                else:
                    logger.error(f"[FATAL] {config['name']} exceeded max restarts")
                    services_status[service_id]['status'] = 'failed'
                    break
            else:
                # Normal exit
                logger.info(f"[STOP] {config['name']} stopped normally")
                services_status[service_id]['status'] = 'stopped'
                break
                
        except Exception as e:
            logger.error(f"[ERROR] {config['name']}: {e}")
            restart_count += 1
            time.sleep(5)


def health_monitor():
    """Monitor health of all services"""
    import urllib.request
    
    logger.info("[MONITOR] Health monitor started")
    
    while True:
        try:
            time.sleep(30)  # Check every 30 seconds
            
            # Check Web Server
            try:
                with urllib.request.urlopen('http://localhost:5000/api/stats', timeout=5) as response:
                    data = json.loads(response.read())
                    interactions = data.get('total_interactions', 0)
                    logger.info(f"[HEALTH] Web Server OK | Interactions: {interactions}")
                    services_status['web_server']['health'] = 'healthy'
            except Exception as e:
                logger.warning(f"[HEALTH] Web Server not responding: {e}")
                services_status['web_server']['health'] = 'unhealthy'
            
            # Log status summary
            status_summary = {k: v.get('status', 'unknown') for k, v in services_status.items()}
            logger.debug(f"[STATUS] {status_summary}")
            
            # Save status file
            save_status_file()
            
        except Exception as e:
            logger.error(f"[MONITOR] Error: {e}")


def save_status_file():
    """Save current status to file"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'services': services_status,
        'summary': {
            'running': sum(1 for s in services_status.values() if s.get('status') == 'running'),
            'failed': sum(1 for s in services_status.values() if s.get('status') == 'failed'),
            'total': len(services_status)
        }
    }
    
    status_file = logs_dir / 'status.json'
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)


def signal_handler(signum, frame):
    """Handle shutdown gracefully"""
    logger.info("="*70)
    logger.info("[SHUTDOWN] Received shutdown signal")
    logger.info("="*70)
    
    for name, process in processes.items():
        try:
            logger.info(f"[SHUTDOWN] Stopping {name} (PID: {process.pid})")
            process.terminate()
            try:
                process.wait(timeout=5)
            except:
                process.kill()
        except Exception as e:
            logger.error(f"[SHUTDOWN] Error stopping {name}: {e}")
    
    logger.info("[SHUTDOWN] All services stopped")
    sys.exit(0)


def create_startup_scripts():
    """Create Windows startup scripts"""
    # Create simple startup batch
    batch_content = '''@echo off
title KUWERA AI - Auto Start
color 0A
cd /d "C:\\AI-Project"
echo.
echo ============================================
echo    KUWERA AI - Starting Services
echo ============================================
echo.
"ai_env\\Scripts\\python.exe" kuwera_autostart.py
echo.
pause
'''
    
    with open('start_kuwera_auto.bat', 'w') as f:
        f.write(batch_content)
    
    logger.info("[OK] Created start_kuwera_auto.bat")
    
    # Create vbs for silent startup
    vbs_content = '''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "C:\\AI-Project\\start_kuwera_auto.bat" & Chr(34), 0
Set WshShell = Nothing
'''
    
    with open('start_kuwera_silent.vbs', 'w') as f:
        f.write(vbs_content)
    
    logger.info("[OK] Created start_kuwera_silent.vbs")


def main():
    """Main entry point"""
    logger.info("")
    logger.info("╔" + "="*68 + "╗")
    logger.info("║" + " "*20 + "KUWERA AI - AUTO START" + " "*26 + "║")
    logger.info("║" + " "*15 + "12 Models | Evolution | Web Interface" + " "*14 + "║")
    logger.info("╚" + "="*68 + "╝")
    logger.info("")
    logger.info(f"Started at: {datetime.now()}")
    logger.info("")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Verify environment
    if not verify_kuwera_environment():
        logger.error("[FATAL] Environment verification failed")
        sys.exit(1)
    
    # Create startup scripts
    create_startup_scripts()
    
    # Start services
    logger.info("")
    logger.info("[INIT] Starting services...")
    logger.info("")
    
    # Start Web Server (main service)
    web_thread = threading.Thread(
        target=start_service,
        args=('web_server', SERVICES['web_server']),
        daemon=True,
        name="WebServer"
    )
    web_thread.start()
    
    time.sleep(3)  # Wait for web server
    
    # Start other services
    for service_id, config in SERVICES.items():
        if service_id == 'web_server':
            continue  # Already started
        
        thread = threading.Thread(
            target=start_service,
            args=(service_id, config),
            daemon=True,
            name=config['name']
        )
        thread.start()
        time.sleep(1)
    
    # Start health monitor
    monitor_thread = threading.Thread(
        target=health_monitor,
        daemon=True,
        name="HealthMonitor"
    )
    monitor_thread.start()
    
    logger.info("")
    logger.info("="*70)
    logger.info("[OK] All services started!")
    logger.info("")
    logger.info("Access URLs:")
    logger.info("  - Web Interface: http://localhost:5000")
    logger.info("  - API: http://localhost:8000 (if enabled)")
    logger.info("")
    logger.info("Commands:")
    logger.info("  - Check health: python kuwera_health_check.py")
    logger.info("  - View logs: logs/kuwera/")
    logger.info("  - Stop: Press Ctrl+C")
    logger.info("="*70)
    logger.info("")
    
    # Keep main thread alive
    try:
        while True:
            save_status_file()
            time.sleep(10)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
