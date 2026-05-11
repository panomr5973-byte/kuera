#!/usr/bin/env python3
"""
KUERA AI — Unified Entry Point v3.1
====================================

Single entry point for the entire KUERA ecosystem.
Replaces: kuera_unified_desktop.py (deprecated)

Usage:
    python main.py

Architecture:
    main.py
        ├── src/core/process_manager.py    (Process lifecycle)
        ├── src/core/service_registry.py   (Service definitions from YAML)
        ├── src/web/dashboard.py           (Flask Control Panel)
        ├── src/utils/config.py            (YAML config loader)
        └── src/utils/logger.py            (Unified logging)
"""

import sys
import threading
import webbrowser
from pathlib import Path
from datetime import datetime

# Ensure src/ is on path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

import json
from src.core.service_registry import load_services
from src.core.process_manager import ProcessManager
from src.core.logger_engine import log_startup, log_shutdown, log_activity
from src.web.dashboard import create_app
from src.models.registry import load_model_registry
from src.utils.config import settings
from src.utils.logger import setup_logger


def load_manifest_info():
    """Load version and phase from KUERA_MANIFEST.json."""
    manifest_path = Path(__file__).parent / "KUERA_MANIFEST.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            return manifest.get("version", "unknown"), manifest.get("phase", 0)
        except Exception:
            pass
    return "unknown", 0


def print_banner(logger):
    """Print startup banner."""
    banner = [
        "=" * 70,
        f"  {settings.app_name} v{settings.app_version}",
        "  Architecture: Modular | Config: YAML | Logs: Unified",
        "=" * 70,
        "",
        f"  Control Panel: http://localhost:{settings.control_panel_port}",
        f"  Working Dir  : {settings.base_dir}",
        "",
        "  Services available:",
    ]
    services = load_services()
    for key, cfg in services.items():
        port_str = f"port {cfg.port}" if cfg.port else "no port"
        banner.append(f"    • {cfg.name} ({port_str})")
    banner.append("")
    banner.append("  Press Ctrl+C to stop all services and exit.")
    banner.append("=" * 70)

    for line in banner:
        print(line)
        logger.info(line)


def main():
    manifest_version, phase = load_manifest_info()
    logger = setup_logger("KUERA-Main")
    logger.info("Starting KUERA AI v%s (Manifest: %s, Phase: %s)", settings.app_version, manifest_version, phase)
    log_startup("KUERA Unified Desktop", f"{settings.app_version} (Phase {phase})")

    services = load_services()
    pm = ProcessManager(services)
    pm.start_monitoring()

    print_banner(logger)
    log_activity("ProcessManager started", {"services_count": len(services)})

    # Auto-open browser
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{settings.control_panel_port}")

    t = threading.Thread(target=open_browser, daemon=True)
    t.start()

    app = create_app(pm, load_model_registry)

    try:
        app.run(
            host="0.0.0.0",
            port=settings.control_panel_port,
            debug=settings.debug,
            use_reloader=False,
        )
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping all services...")
        logger.info("KeyboardInterrupt received. Shutting down.")
    finally:
        pm.stop_all()
        log_shutdown("Graceful exit via KeyboardInterrupt or signal")
        print("[SHUTDOWN] All services stopped. Goodbye!")
        logger.info("Shutdown complete.")


if __name__ == "__main__":
    main()
