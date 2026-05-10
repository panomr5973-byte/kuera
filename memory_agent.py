#!/usr/bin/env python3
"""
KUERA Automated Memory Agent
Auto-catat aktivitas ke file memory saat unified desktop dijalankan/ditutup.

Usage:
    from memory_agent import MemoryAgent
    agent = MemoryAgent()
    agent.log_startup()
    # ... do work ...
    agent.log_shutdown(summary="Services started: API, Web")
"""

import json
import sys
import os
import socket
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class MemoryAgent:
    """Automated memory logging for KUERA AI workspace."""
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.memory_file = self.memory_dir / f"{self.today}.md"
        self.meta_file = self.memory_dir / ".meta.json"
        self._load_meta()
    
    def _load_meta(self):
        """Load session metadata."""
        if self.meta_file.exists():
            try:
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    self.meta = json.load(f)
            except:
                self.meta = {"sessions": [], "total_sessions": 0}
        else:
            self.meta = {"sessions": [], "total_sessions": 0}
    
    def _save_meta(self):
        """Save session metadata."""
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, indent=2, ensure_ascii=False)
    
    def _get_memory_header(self) -> str:
        """Generate memory file header if new."""
        if not self.memory_file.exists():
            return f"# Memory Log - {self.today}\n\n"
        return ""
    
    def _detect_services(self) -> Dict[str, bool]:
        """Detect which services are running on their ports."""
        services = {
            "api_production": 8000,
            "api_real": 8001,
            "web_flask": 5000,
            "dashboard_streamlit": 8501,
            "unified_desktop": 7777,
            "gateway": 18789,
        }
        status = {}
        for name, port in services.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("127.0.0.1", port))
                status[name] = (result == 0)
                sock.close()
            except:
                status[name] = False
        return status
    
    def _get_git_status(self) -> str:
        """Get short git status."""
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True, text=True, timeout=5, cwd=Path(__file__).parent
            )
            lines = result.stdout.strip().split("\n")
            changed = len([l for l in lines if l.strip()])
            return f"{changed} file(s) changed"
        except:
            return "unknown"
    
    def _append_to_memory(self, content: str):
        """Append content to today's memory file."""
        header = self._get_memory_header()
        with open(self.memory_file, "a", encoding="utf-8") as f:
            if header:
                f.write(header)
            f.write(content)
            f.write("\n")
    
    def log_startup(self, note: str = ""):
        """Log when unified desktop starts."""
        services = self._detect_services()
        running = [k for k, v in services.items() if v]
        
        content = f"""## Session Start — {datetime.now().strftime("%H:%M")}

- **Services already running**: {', '.join(running) if running else 'none'}
- **Note**: {note or 'Unified desktop starting'}
- **Git status**: {self._get_git_status()}

"""
        self._append_to_memory(content)
        
        # Update meta
        self.meta["sessions"].append({
            "date": self.today,
            "time": datetime.now().strftime("%H:%M"),
            "event": "startup",
            "note": note
        })
        self.meta["total_sessions"] += 1
        self._save_meta()
    
    def log_shutdown(self, summary: str = "", services_started: List[str] = None):
        """Log when unified desktop shuts down."""
        services = self._detect_services()
        still_running = [k for k, v in services.items() if v]
        
        content = f"""## Session End — {datetime.now().strftime("%H:%M")}

- **Summary**: {summary or 'Session ended'}
- **Services started this session**: {', '.join(services_started) if services_started else 'none recorded'}
- **Still running**: {', '.join(still_running) if still_running else 'none'}
- **Git status**: {self._get_git_status()}

---

"""
        self._append_to_memory(content)
        
        # Update meta
        self.meta["sessions"].append({
            "date": self.today,
            "time": datetime.now().strftime("%H:%M"),
            "event": "shutdown",
            "summary": summary
        })
        self._save_meta()
    
    def log_event(self, category: str, description: str, detail: str = ""):
        """Log an arbitrary event."""
        content = f"""### [{category}] {datetime.now().strftime("%H:%M")}

{description}

"""
        if detail:
            content += f"```\n{detail}\n```\n\n"
        
        self._append_to_memory(content)
    
    def log_error(self, error_msg: str, context: str = ""):
        """Log an error with context."""
        content = f"""### [ERROR] {datetime.now().strftime("%H:%M")}

**Message**: {error_msg}

"""
        if context:
            content += f"**Context**: {context}\n\n"
        
        self._append_to_memory(content)


def inject_to_unified_desktop():
    """
    Modify kuera_unified_desktop.py to include memory agent hooks.
    This is a one-time injection.
    """
    unified_file = Path("kuera_unified_desktop.py")
    if not unified_file.exists():
        print("[ERROR] kuera_unified_desktop.py not found")
        return False
    
    with open(unified_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if already injected
    if "from memory_agent import MemoryAgent" in content:
        print("[INFO] Memory agent already injected")
        return True
    
    # Inject import after the last import
    import_idx = content.rfind("import ")
    if import_idx == -1:
        print("[ERROR] Could not find import section")
        return False
    
    # Find end of that line
    line_end = content.find("\n", import_idx)
    inject_import = '\nfrom memory_agent import MemoryAgent\n'
    content = content[:line_end+1] + inject_import + content[line_end+1:]
    
    # Inject startup hook in main() before pm.start_monitoring()
    startup_hook = '''    # Initialize memory agent
    mem_agent = MemoryAgent()
    mem_agent.log_startup("KUERA Unified Desktop v3.0")
    
'''
    content = content.replace(
        "    pm.start_monitoring()",
        startup_hook + "    pm.start_monitoring()"
    )
    
    # Inject shutdown hook in finally block
    shutdown_hook = '''        # Log shutdown
        mem_agent.log_shutdown("All services stopped")
    
'''
    content = content.replace(
        "        pm.stop_all()",
        "        mem_agent.log_shutdown(\"All services stopped\")\n        pm.stop_all()"
    )
    
    with open(unified_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("[OK] Memory agent injected into kuera_unified_desktop.py")
    return True


if __name__ == "__main__":
    # Demo usage
    agent = MemoryAgent()
    agent.log_startup("Manual test of memory agent")
    agent.log_event("TEST", "Memory agent is working correctly")
    agent.log_shutdown("Test complete")
    print(f"[OK] Memory written to: {agent.memory_file}")
