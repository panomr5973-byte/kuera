"""KUERA AI — Process Manager.

Manages lifecycle of subprocess services: start, stop, restart, monitor,
and auto-restart on crash. Thread-safe via RLock.
"""

import os
import sys
import time
import socket
import logging
import subprocess
import threading
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from ..utils.config import BASE_DIR, settings
from .service_registry import ServiceConfig

logger = logging.getLogger("KUERA-ProcessManager")


@dataclass
class ServiceStatus:
    name: str
    pid: Optional[int] = None
    state: str = "stopped"  # running, stopped, crashed, starting
    uptime: str = "0s"
    restarts: int = 0
    last_log: str = ""
    port: Optional[int] = None
    health: str = "unknown"  # healthy, unhealthy, unknown


class ProcessManager:
    """Manages subprocess services with health monitoring and auto-restart."""

    def __init__(self, services: Dict[str, ServiceConfig]):
        self.services = services
        self.processes: Dict[str, subprocess.Popen] = {}
        self.statuses: Dict[str, ServiceStatus] = {}
        self.start_times: Dict[str, float] = {}
        self.restart_counts: Dict[str, int] = {k: 0 for k in services}
        self.log_buffers: Dict[str, List[str]] = {k: [] for k in services}
        self._lock = threading.RLock()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        python_exec = str(BASE_DIR / "ai_env" / "Scripts" / "python.exe")
        self._python_exec = python_exec if Path(python_exec).exists() else sys.executable

        self._init_statuses()

    def _init_statuses(self):
        for key, cfg in self.services.items():
            self.statuses[key] = ServiceStatus(
                name=cfg.name,
                port=cfg.port,
            )

    def start_service(self, key: str) -> bool:
        with self._lock:
            if key in self.processes and self.processes[key].poll() is None:
                logger.warning("[%s] Already running (PID %d)", key, self.processes[key].pid)
                return False

            cfg = self.services[key]
            env = os.environ.copy()
            if cfg.env:
                env.update(cfg.env)

            if cfg.args:
                cmd = [self._python_exec] + cfg.args
            else:
                cmd = [self._python_exec, str(cfg.script_path)]

            wd = cfg.working_dir or str(BASE_DIR)

            try:
                logger.info("[%s] Starting: %s", key, " ".join(cmd))
                proc = subprocess.Popen(
                    cmd,
                    cwd=wd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
                )
                self.processes[key] = proc
                self.start_times[key] = time.time()
                self.statuses[key].pid = proc.pid
                self.statuses[key].state = "running"
                self.statuses[key].health = "healthy"

                t = threading.Thread(target=self._log_reader, args=(key, proc), daemon=True)
                t.start()
                return True
            except Exception as e:
                logger.error("[%s] Failed to start: %s", key, e)
                self.statuses[key].state = "crashed"
                self.statuses[key].health = "unhealthy"
                return False

    def stop_service(self, key: str) -> bool:
        with self._lock:
            if key not in self.processes:
                return False
            proc = self.processes[key]
            try:
                logger.info("[%s] Stopping PID %d...", key, proc.pid)
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                self.statuses[key].state = "stopped"
                self.statuses[key].pid = None
                self.statuses[key].health = "unknown"
                logger.info("[%s] Stopped.", key)
                return True
            except Exception as e:
                logger.error("[%s] Error stopping: %s", key, e)
                return False

    def restart_service(self, key: str) -> bool:
        self.stop_service(key)
        time.sleep(1)
        return self.start_service(key)

    def _log_reader(self, key: str, proc: subprocess.Popen):
        try:
            for line in iter(proc.stdout.readline, ""):
                if not line:
                    break
                line = line.rstrip()
                self.log_buffers[key].append(line)
                if len(self.log_buffers[key]) > settings._data.get("logging", {}).get("max_log_buffer", 500):
                    self.log_buffers[key] = self.log_buffers[key][-settings._data.get("logging", {}).get("log_history_lines", 250):]
                self.statuses[key].last_log = line[:200]
        except Exception as e:
            logger.error("[%s] Log reader error: %s", key, e)

    def _monitor_loop(self):
        interval = settings._data.get("services", {}).get("health_check_interval", 3)
        while not self._stop_event.is_set():
            for key in self.services:
                cfg = self.services[key]
                st = self.statuses[key]

                if key in self.processes:
                    proc = self.processes[key]
                    ret = proc.poll()

                    if ret is not None and st.state == "running":
                        st.state = "crashed"
                        st.health = "unhealthy"
                        logger.warning("[%s] Process exited with code %d", key, ret)

                        if cfg.restart_on_crash and self.restart_counts[key] < cfg.max_restarts:
                            self.restart_counts[key] += 1
                            st.restarts = self.restart_counts[key]
                            logger.info("[%s] Auto-restarting (%d/%d)...", key, st.restarts, cfg.max_restarts)
                            self.start_service(key)

                    elif ret is None and st.state == "running":
                        uptime_sec = int(time.time() - self.start_times.get(key, time.time()))
                        st.uptime = self._fmt_duration(uptime_sec)

                        if cfg.port:
                            st.health = "healthy" if self._probe_port(cfg.port) else "unhealthy"

            self._stop_event.wait(interval)

    @staticmethod
    def _probe_port(port: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                return s.connect_ex(("127.0.0.1", port)) == 0
        except Exception:
            return False

    @staticmethod
    def _fmt_duration(secs: int) -> str:
        if secs < 60:
            return f"{secs}s"
        if secs < 3600:
            return f"{secs//60}m {secs%60}s"
        return f"{secs//3600}h {(secs%3600)//60}m"

    def start_monitoring(self):
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Process monitor started.")

    def stop_all(self):
        self._stop_event.set()
        for key in list(self.processes.keys()):
            self.stop_service(key)

    def get_all_status(self) -> Dict[str, dict]:
        with self._lock:
            return {k: asdict(v) for k, v in self.statuses.items()}

    def get_logs(self, key: str, lines: int = 50) -> List[str]:
        return self.log_buffers.get(key, [])[-lines:]
