#!/usr/bin/env python3
"""KUERA AI — Logger Engine (Memory Injection)

Automatically logs system activities to daily memory files.
Import this into main.py or any service to track runtime state.

Usage:
    from src.core.logger_engine import log_activity, log_startup, log_shutdown
    log_startup("KUERA Unified Desktop v3.1")
    log_activity("Audit workflow completed: 3 files processed")
    log_shutdown("Graceful exit after 2h 14m")
"""

import os
import sys
import platform
import psutil
from pathlib import Path
from datetime import datetime
from typing import Optional

BASE_DIR = Path(__file__).parent.parent.parent.resolve()
MEMORY_DIR = BASE_DIR / "memory"


def _ensure_memory_dir():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def _get_memory_path(date: Optional[datetime] = None) -> Path:
    date = date or datetime.now()
    return MEMORY_DIR / f"{date.strftime('%Y-%m-%d')}.md"


def _get_timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _system_snapshot() -> dict:
    """Collect lightweight system metrics."""
    try:
        mem = psutil.virtual_memory()
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram_used_gb": mem.used / (1024 ** 3),
            "ram_total_gb": mem.total / (1024 ** 3),
            "ram_percent": mem.percent,
            "platform": platform.platform(),
            "python_version": sys.version.split()[0],
        }
    except Exception:
        return {}


def log_startup(system_name: str = "KUERA", version: str = "3.1"):
    """Log system startup with system snapshot."""
    _ensure_memory_dir()
    path = _get_memory_path()
    ts = _get_timestamp()
    snap = _system_snapshot()
    
    header = f"# {system_name} Daily Log — {datetime.now().strftime('%d %B %Y')}\n\n"
    
    lines = [
        f"## [{ts}] 🚀 SYSTEM STARTUP\n",
        f"- **System:** {system_name} v{version}\n",
        f"- **Timestamp:** {datetime.now().isoformat()}\n",
    ]
    
    if snap:
        lines.append(f"- **Platform:** {snap.get('platform', 'N/A')}\n")
        lines.append(f"- **Python:** {snap.get('python_version', 'N/A')}\n")
        lines.append(f"- **RAM:** {snap.get('ram_used_gb', 0):.1f} / {snap.get('ram_total_gb', 0):.1f} GB ({snap.get('ram_percent', 0)}%)\n")
        lines.append(f"- **CPU:** {snap.get('cpu_percent', 0)}%\n")
    
    lines.append("\n")
    
    if not path.exists():
        path.write_text(header + "".join(lines), encoding="utf-8")
    else:
        with open(path, "a", encoding="utf-8") as f:
            f.write("".join(lines))


def log_activity(summary: str, details: Optional[dict] = None):
    """Log a system activity to today's memory file.
    
    Args:
        summary: Short description of the activity
        details: Optional dict with additional metadata
    """
    _ensure_memory_dir()
    path = _get_memory_path()
    ts = _get_timestamp()
    
    lines = [f"## [{ts}] ⚡ ACTIVITY\n", f"- {summary}\n"]
    
    if details:
        for key, value in details.items():
            lines.append(f"  - **{key}:** {value}\n")
    
    lines.append("\n")
    
    if not path.exists():
        header = f"# KUERA Daily Log — {datetime.now().strftime('%d %B %Y')}\n\n"
        path.write_text(header + "".join(lines), encoding="utf-8")
    else:
        with open(path, "a", encoding="utf-8") as f:
            f.write("".join(lines))


def log_error(error_msg: str, source: str = "unknown"):
    """Log an error to today's memory file."""
    _ensure_memory_dir()
    path = _get_memory_path()
    ts = _get_timestamp()
    
    lines = [
        f"## [{ts}] ❌ ERROR\n",
        f"- **Source:** {source}\n",
        f"- **Message:** {error_msg}\n",
        f"- **Time:** {datetime.now().isoformat()}\n",
        "\n",
    ]
    
    if not path.exists():
        header = f"# KUERA Daily Log — {datetime.now().strftime('%d %B %Y')}\n\n"
        path.write_text(header + "".join(lines), encoding="utf-8")
    else:
        with open(path, "a", encoding="utf-8") as f:
            f.write("".join(lines))


def log_shutdown(reason: str = "Graceful exit"):
    """Log system shutdown."""
    _ensure_memory_dir()
    path = _get_memory_path()
    ts = _get_timestamp()
    
    lines = [
        f"## [{ts}] 🛑 SYSTEM SHUTDOWN\n",
        f"- **Reason:** {reason}\n",
        f"- **Time:** {datetime.now().isoformat()}\n",
        "\n",
    ]
    
    if not path.exists():
        header = f"# KUERA Daily Log — {datetime.now().strftime('%d %B %Y')}\n\n"
        path.write_text(header + "".join(lines), encoding="utf-8")
    else:
        with open(path, "a", encoding="utf-8") as f:
            f.write("".join(lines))


def get_today_log_path() -> Path:
    """Return the path to today's memory file."""
    return _get_memory_path()


if __name__ == "__main__":
    # Test run
    log_startup("KUERA Test", "3.1")
    log_activity("Sanitizer executed", {"files_archived": 42, "mode": "live"})
    log_shutdown("Test complete")
    print(f"Log written to: {get_today_log_path()}")
