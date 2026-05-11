#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  KUERA UNIFIED DESKTOP v3.0
  Integrasi: KueraClaw | Kuera-AI Evolusi | Kuera API | Admin Panel
═══════════════════════════════════════════════════════════════════════════════

Fitur Utama:
  • Single-process orchestrator untuk semua services
  • Web Control Panel di http://localhost:7777
  • Health monitoring & auto-restart
  • Unified logging & status tracking
  • Model registry integration
  • Evolution tracking dashboard

Usage:
  python kuera_unified_desktop.py
"""

import os
import sys
import json
import time
import logging
import subprocess
import threading
import webbrowser
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any

# Flask imports
from flask import Flask, render_template_string, jsonify, request, send_from_directory
from flask_cors import CORS

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
LOGS_DIR = BASE_DIR / "logs" / "unified"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

CONTROL_PANEL_PORT = 7777
SERVICE_PORTS = {
    "api_production": 8000,
    "api_real": 8001,
    "web_flask": 5000,
    "dashboard_streamlit": 8501,
    "web_http": 8080,
}

# ─── LOGGING SETUP ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / f"unified_{datetime.now():%Y%m%d}.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("KUERA-UNIFIED")

# ─── DATA CLASSES ────────────────────────────────────────────────────────────
@dataclass
class ServiceConfig:
    name: str
    script: str
    port: Optional[int]
    auto_start: bool = True
    restart_on_crash: bool = True
    max_restarts: int = 5
    env: Dict[str, str] = None
    args: List[str] = None
    working_dir: str = None

@dataclass
class ServiceStatus:
    name: str
    pid: Optional[int]
    state: str  # running, stopped, crashed, starting
    uptime: str
    restarts: int
    last_log: str
    port: Optional[int]
    health: str  # healthy, unhealthy, unknown

# ─── SERVICE DEFINITIONS ─────────────────────────────────────────────────────
SERVICES: Dict[str, ServiceConfig] = {
    "kuera_api": ServiceConfig(
        name="Kuera Production API",
        script=str(BASE_DIR / "start_api.py"),
        port=SERVICE_PORTS["api_production"],
        auto_start=False,
        restart_on_crash=True,
    ),
    "kuera_real_api": ServiceConfig(
        name="Kuera Real API (8001)",
        script=str(BASE_DIR / "app" / "real_api.py"),
        port=SERVICE_PORTS["api_real"],
        auto_start=False,
        restart_on_crash=True,
        args=["-m", "uvicorn", "app.real_api:app", "--host", "0.0.0.0", "--port", "8001"]
    ),
    "kuera_web_v2": ServiceConfig(
        name="Kuera Web Server v2",
        script=str(BASE_DIR / "kuwera_web_server_v2.py"),
        port=SERVICE_PORTS["web_flask"],
        auto_start=False,
        restart_on_crash=True,
    ),
    "kuera_dashboard": ServiceConfig(
        name="Kuera Streamlit Dashboard",
        script=str(BASE_DIR / "start_dashboard.py"),
        port=SERVICE_PORTS["dashboard_streamlit"],
        auto_start=False,
        restart_on_crash=False,
    ),
    "kuera_admin": ServiceConfig(
        name="Kuera Admin Panel",
        script=str(BASE_DIR / "admin_panel" / "start_admin.py"),
        port=SERVICE_PORTS["web_flask"],
        auto_start=False,
        restart_on_crash=True,
    ),
    "kuera_evolution": ServiceConfig(
        name="Kuera Evolution Engine",
        script=str(BASE_DIR / "kuera_evolution_engine.py"),
        port=None,
        auto_start=False,
        restart_on_crash=True,
    ),
    "kuera_claw": ServiceConfig(
        name="KueraClaw Multi-Model CLI",
        script=str(BASE_DIR / "kuera_integrated_system.py"),
        port=None,
        auto_start=False,
        restart_on_crash=False,
    ),
}

# ─── PROCESS MANAGER ─────────────────────────────────────────────────────────
class ProcessManager:
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.statuses: Dict[str, ServiceStatus] = {}
        self.start_times: Dict[str, float] = {}
        self.restart_counts: Dict[str, int] = {k: 0 for k in SERVICES}
        self.log_buffers: Dict[str, List[str]] = {k: [] for k in SERVICES}
        self._lock = threading.RLock()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        for key in SERVICES:
            self.statuses[key] = ServiceStatus(
                name=SERVICES[key].name,
                pid=None,
                state="stopped",
                uptime="0s",
                restarts=0,
                last_log="",
                port=SERVICES[key].port,
                health="unknown"
            )
    
    def start_service(self, key: str) -> bool:
        with self._lock:
            if key in self.processes and self.processes[key].poll() is None:
                logger.warning(f"[{key}] Already running (PID {self.processes[key].pid})")
                return False
            
            cfg = SERVICES[key]
            python_exec = str(BASE_DIR / "ai_env" / "Scripts" / "python.exe")
            if not Path(python_exec).exists():
                python_exec = sys.executable
            
            env = os.environ.copy()
            if cfg.env:
                env.update(cfg.env)
            
            cmd = [python_exec]
            if cfg.args:
                cmd = [python_exec] + cfg.args
            else:
                cmd = [python_exec, cfg.script]
            
            wd = cfg.working_dir or str(BASE_DIR)
            
            try:
                logger.info(f"[{key}] Starting: {' '.join(cmd)}")
                proc = subprocess.Popen(
                    cmd,
                    cwd=wd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
                )
                self.processes[key] = proc
                self.start_times[key] = time.time()
                self.statuses[key].pid = proc.pid
                self.statuses[key].state = "running"
                self.statuses[key].health = "healthy"
                
                # Start log reader thread
                t = threading.Thread(target=self._log_reader, args=(key, proc), daemon=True)
                t.start()
                
                return True
            except Exception as e:
                logger.error(f"[{key}] Failed to start: {e}")
                self.statuses[key].state = "crashed"
                self.statuses[key].health = "unhealthy"
                return False
    
    def stop_service(self, key: str) -> bool:
        with self._lock:
            if key not in self.processes:
                return False
            proc = self.processes[key]
            try:
                logger.info(f"[{key}] Stopping PID {proc.pid}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                self.statuses[key].state = "stopped"
                self.statuses[key].pid = None
                self.statuses[key].health = "unknown"
                logger.info(f"[{key}] Stopped.")
                return True
            except Exception as e:
                logger.error(f"[{key}] Error stopping: {e}")
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
                if len(self.log_buffers[key]) > 500:
                    self.log_buffers[key] = self.log_buffers[key][-250:]
                self.statuses[key].last_log = line[:200]
        except Exception as e:
            logger.error(f"[{key}] Log reader error: {e}")
    
    def _monitor_loop(self):
        while not self._stop_event.is_set():
            for key in SERVICES:
                cfg = SERVICES[key]
                st = self.statuses[key]
                
                if key in self.processes:
                    proc = self.processes[key]
                    ret = proc.poll()
                    
                    if ret is not None and st.state == "running":
                        st.state = "crashed"
                        st.health = "unhealthy"
                        logger.warning(f"[{key}] Process exited with code {ret}")
                        
                        if cfg.restart_on_crash and self.restart_counts[key] < cfg.max_restarts:
                            self.restart_counts[key] += 1
                            st.restarts = self.restart_counts[key]
                            logger.info(f"[{key}] Auto-restarting ({st.restarts}/{cfg.max_restarts})...")
                            self.start_service(key)
                    
                    elif ret is None and st.state == "running":
                        uptime_sec = int(time.time() - self.start_times.get(key, time.time()))
                        st.uptime = self._fmt_duration(uptime_sec)
                        
                        # Simple health check via port
                        if cfg.port:
                            import socket

from memory_agent import MemoryAgent
                            try:
                                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                s.settimeout(2)
                                s.connect(("127.0.0.1", cfg.port))
                                s.close()
                                st.health = "healthy"
                            except:
                                st.health = "unhealthy"
            
            self._stop_event.wait(3)
    
    def _fmt_duration(self, secs: int) -> str:
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

# ─── MODEL REGISTRY LOADER ───────────────────────────────────────────────────
def load_model_registry() -> Dict[str, Any]:
    reg_path = BASE_DIR / "models" / "llm" / "model_registry_active.json"
    if reg_path.exists():
        try:
            with open(reg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
    return {"models": [], "total_models": 0, "total_size_gb": 0}

# ─── FLASK APP ───────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)
pm = ProcessManager()

# ─── HTML DASHBOARD TEMPLATE ─────────────────────────────────────────────────
CONTROL_PANEL_HTML = r"""
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KUERA Unified Control Panel v3.0</title>
<style>
  :root {
    --bg: #0f172a; --card: #1e293b; --accent: #06b6d4;
    --success: #22c55e; --danger: #ef4444; --warn: #eab308;
    --text: #e2e8f0; --muted: #94a3b8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: var(--bg); color: var(--text);
    min-height: 100vh;
  }
  header {
    background: linear-gradient(90deg, #0891b2, #06b6d4);
    padding: 1.2rem 2rem;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 4px 20px rgba(6,182,212,0.3);
  }
  header h1 { font-size: 1.4rem; display: flex; align-items: center; gap: 0.6rem; }
  header .badge {
    background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem;
    border-radius: 999px; font-size: 0.75rem; font-weight: 600;
  }
  .container { max-width: 1400px; margin: 0 auto; padding: 1.5rem; }
  .grid { display: grid; gap: 1.2rem; }
  .grid-4 { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
  .grid-2 { grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); }
  .card {
    background: var(--card); border-radius: 12px;
    padding: 1.2rem; border: 1px solid #334155;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
  .card h3 { font-size: 0.85rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
  .metric { font-size: 2rem; font-weight: 700; color: var(--accent); }
  .status-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
  .status-running { background: var(--success); box-shadow: 0 0 8px var(--success); }
  .status-stopped { background: var(--muted); }
  .status-crashed { background: var(--danger); box-shadow: 0 0 8px var(--danger); }
  .status-starting { background: var(--warn); animation: pulse 1.5s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  .service-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.9rem 1rem; background: #0f172a; border-radius: 8px;
    margin-bottom: 0.6rem; border: 1px solid #334155;
  }
  .service-info { display: flex; align-items: center; gap: 0.8rem; }
  .service-name { font-weight: 600; }
  .service-meta { font-size: 0.8rem; color: var(--muted); }
  .btn {
    border: none; padding: 0.45rem 1rem; border-radius: 6px;
    font-size: 0.8rem; font-weight: 600; cursor: pointer;
    transition: all 0.2s; text-transform: uppercase; letter-spacing: 0.03em;
  }
  .btn-start { background: var(--success); color: #064e3b; }
  .btn-stop { background: var(--danger); color: #450a0a; }
  .btn-restart { background: var(--warn); color: #422006; }
  .btn:hover { opacity: 0.85; transform: scale(1.03); }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

  .log-box {
    background: #020617; color: #a5f3fc; font-family: 'Fira Code', monospace;
    padding: 1rem; border-radius: 8px; height: 300px; overflow-y: auto;
    font-size: 0.82rem; line-height: 1.5; border: 1px solid #334155;
  }
  .log-box .ts { color: #64748b; margin-right: 0.5rem; }
  .log-box .err { color: #fca5a5; }
  .log-box .warn { color: #fde047; }

  .model-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.8rem; }
  .model-card {
    background: #0f172a; border: 1px solid #334155; border-radius: 8px;
    padding: 0.8rem; text-align: center;
  }
  .model-card .model-name { font-size: 0.85rem; font-weight: 600; color: var(--accent); }
  .model-card .model-size { font-size: 0.75rem; color: var(--muted); margin-top: 0.3rem; }
  .model-card .model-lang { font-size: 0.7rem; background: #334155; display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px; margin-top: 0.4rem; }

  .quick-links { display: flex; gap: 0.6rem; flex-wrap: wrap; }
  .quick-links a {
    background: #0f172a; color: var(--accent); text-decoration: none;
    padding: 0.5rem 1rem; border-radius: 6px; border: 1px solid #334155;
    font-size: 0.85rem; transition: all 0.2s;
  }
  .quick-links a:hover { background: var(--accent); color: #0f172a; }

  .section-title {
    font-size: 1.1rem; font-weight: 700; margin: 1.5rem 0 0.8rem;
    display: flex; align-items: center; gap: 0.5rem;
  }
  footer {
    text-align: center; padding: 2rem; color: var(--muted); font-size: 0.8rem;
    border-top: 1px solid #334155; margin-top: 2rem;
  }
  .toast {
    position: fixed; bottom: 1.5rem; right: 1.5rem;
    background: var(--card); color: var(--text); padding: 1rem 1.5rem;
    border-radius: 8px; border-left: 4px solid var(--accent);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4); transform: translateX(150%);
    transition: transform 0.3s ease; z-index: 1000; font-size: 0.9rem;
  }
  .toast.show { transform: translateX(0); }
</style>
</head>
<body>
<header>
  <h1>🧠 KUERA Unified Control Panel <span style="font-weight:400;opacity:0.9">v3.0</span></h1>
  <div style="display:flex;gap:0.8rem;align-items:center;">
    <span class="badge" id="global-status">Initializing...</span>
    <span class="badge" id="uptime-badge">Uptime: 0s</span>
  </div>
</header>

<div class="container">

  <!-- Quick Stats -->
  <div class="grid grid-4" style="margin-bottom:1.5rem;">
    <div class="card">
      <h3>Active Services</h3>
      <div class="metric" id="stat-active">0</div>
    </div>
    <div class="card">
      <h3>Total Models</h3>
      <div class="metric" id="stat-models">0</div>
    </div>
    <div class="card">
      <h3>Registry Size</h3>
      <div class="metric" id="stat-size">0 GB</div>
    </div>
    <div class="card">
      <h3>System Health</h3>
      <div class="metric" id="stat-health" style="font-size:1.4rem;display:flex;align-items:center;gap:0.5rem;">
        <span class="status-dot status-stopped"></span> Unknown
      </div>
    </div>
  </div>

  <!-- Quick Links -->
  <div class="card" style="margin-bottom:1.5rem;">
    <h3 style="margin-bottom:0.8rem;">Quick Access</h3>
    <div class="quick-links">
      <a href="http://localhost:5000" target="_blank">🌐 Web Interface v2</a>
      <a href="http://localhost:8000/docs" target="_blank">📡 API Docs (8000)</a>
      <a href="http://localhost:8501" target="_blank">📊 Streamlit Dashboard</a>
      <a href="http://localhost:8001/docs" target="_blank">📡 Real API (8001)</a>
      <a href="http://localhost:5000" target="_blank">🛡️ Admin Panel</a>
      <a href="#" onclick="alert('Use Start button on Service Manager');return false;">⚡ Evolution Engine</a>
      <a href="#" onclick="alert('Use Start button on Service Manager');return false;">🦾 KueraClaw CLI</a>
    </div>
  </div>

  <!-- Service Manager -->
  <div class="section-title">⚙️ Service Manager</div>
  <div class="card" id="services-container">
    <div style="text-align:center;padding:2rem;color:var(--muted);">Loading services...</div>
  </div>

  <!-- Logs -->
  <div class="section-title">📜 Unified Logs</div>
  <div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;">
      <span style="font-size:0.85rem;color:var(--muted);">Real-time log aggregation</span>
      <select id="log-service" onchange="loadLogs()" style="background:#0f172a;color:var(--text);border:1px solid #334155;padding:0.3rem 0.6rem;border-radius:4px;">
        <option value="all">All Services</option>
      </select>
    </div>
    <div class="log-box" id="log-box">Waiting for logs...</div>
  </div>

  <!-- Model Registry -->
  <div class="section-title">🤖 Model Registry</div>
  <div class="card" id="models-container">
    <div style="text-align:center;padding:2rem;color:var(--muted);">Loading models...</div>
  </div>

</div>

<div class="toast" id="toast"></div>

<footer>
  KUERA Unified Desktop v3.0 | Integrated Multi-Model AI System<br>
  KueraClaw + Kuera-AI Evolusi + Kuera API | D:\workspace\ai_core\AI-Project
</footer>

<script>
let serviceKeys = [];
let uptimeStart = Date.now();

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

async function api(path, opts={}) {
  try {
    const r = await fetch(path, opts);
    return await r.json();
  } catch(e) { console.error(e); return {}; }
}

function statusDot(state) {
  const cls = state==='running'?'status-running':state==='crashed'?'status-crashed':state==='starting'?'status-starting':'status-stopped';
  return `<span class="status-dot ${cls}"></span>`;
}

async function refreshServices() {
  const data = await api('/api/services');
  const container = document.getElementById('services-container');
  const logSelect = document.getElementById('log-service');
  serviceKeys = Object.keys(data);
  
  // Update log dropdown
  const currentVal = logSelect.value;
  logSelect.innerHTML = '<option value="all">All Services</option>' + 
    serviceKeys.map(k => `<option value="${k}">${data[k].name}</option>`).join('');
  if ([...logSelect.options].some(o=>o.value===currentVal)) logSelect.value = currentVal;

  let activeCount = 0;
  let html = '';
  for (const [key, s] of Object.entries(data)) {
    if (s.state === 'running') activeCount++;
    const actions = s.state==='running'
      ? `<button class="btn btn-stop" onclick="control('${key}','stop')">Stop</button> <button class="btn btn-restart" onclick="control('${key}','restart')">Restart</button>`
      : `<button class="btn btn-start" onclick="control('${key}','start')">Start</button>`;
    html += `
      <div class="service-row">
        <div class="service-info">
          ${statusDot(s.state)}
          <div>
            <div class="service-name">${s.name}</div>
            <div class="service-meta">PID: ${s.pid||'-'} | Uptime: ${s.uptime} | Restarts: ${s.restarts} | Port: ${s.port||'N/A'} | Health: ${s.health}</div>
          </div>
        </div>
        <div style="display:flex;gap:0.4rem;">${actions}</div>
      </div>
    `;
  }
  container.innerHTML = html;
  
  document.getElementById('stat-active').textContent = activeCount;
  
  const healthDot = document.getElementById('stat-health');
  if (activeCount === serviceKeys.length) {
    healthDot.innerHTML = '<span class="status-dot status-running"></span> Optimal';
    document.getElementById('global-status').textContent = 'All Systems Operational';
    document.getElementById('global-status').style.background = 'rgba(34,197,94,0.25)';
    document.getElementById('global-status').style.color = '#86efac';
  } else if (activeCount > 0) {
    healthDot.innerHTML = '<span class="status-dot status-starting"></span> Degraded';
    document.getElementById('global-status').textContent = 'Partial Operation';
    document.getElementById('global-status').style.background = 'rgba(234,179,8,0.25)';
    document.getElementById('global-status').style.color = '#fde047';
  } else {
    healthDot.innerHTML = '<span class="status-dot status-stopped"></span> Standby';
    document.getElementById('global-status').textContent = 'Standby Mode';
    document.getElementById('global-status').style.background = 'rgba(148,163,184,0.25)';
    document.getElementById('global-status').style.color = '#cbd5e1';
  }
}

async function control(key, action) {
  showToast(`${action.charAt(0).toUpperCase()+action.slice(1)}ing ${key}...`);
  const data = await api(`/api/services/${key}/${action}`, {method:'POST'});
  showToast(data.message || 'Done');
  setTimeout(refreshServices, 500);
}

async function loadLogs() {
  const svc = document.getElementById('log-service').value;
  const data = await api(`/api/logs?service=${svc}&lines=100`);
  const box = document.getElementById('log-box');
  if (!data.logs || data.logs.length === 0) {
    box.innerHTML = '<span style="color:#64748b">No logs available yet.</span>';
    return;
  }
  box.innerHTML = data.logs.map(l => {
    let cls = '';
    if (/error|fail|exception|traceback/i.test(l)) cls = 'err';
    else if (/warn|warning|caution/i.test(l)) cls = 'warn';
    return `<div class="${cls}">${l.replace(/</g,'&lt;')}</div>`;
  }).join('');
  box.scrollTop = box.scrollHeight;
}

async function loadModels() {
  const data = await api('/api/models');
  const container = document.getElementById('models-container');
  document.getElementById('stat-models').textContent = data.total_models || 0;
  document.getElementById('stat-size').textContent = (data.total_size_gb || 0).toFixed(2) + ' GB';
  
  if (!data.models || data.models.length === 0) {
    container.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--muted);">No models registered. Place .gguf files in models/llm/</div>';
    return;
  }
  container.innerHTML = '<div class="model-grid">' + data.models.map(m => `
    <div class="model-card">
      <div class="model-name">${m.name}</div>
      <div class="model-size">${m.size_gb} GB</div>
      <div class="model-lang">${m.language}</div>
      <div style="font-size:0.7rem;color:var(--muted);margin-top:0.3rem;">${m.developer}</div>
    </div>
  `).join('') + '</div>';
}

function updateUptime() {
  const sec = Math.floor((Date.now() - uptimeStart) / 1000);
  const m = Math.floor(sec / 60), s = sec % 60;
  document.getElementById('uptime-badge').textContent = `Uptime: ${m}m ${s}s`;
}

// Init
(async () => {
  await refreshServices();
  await loadModels();
  setInterval(refreshServices, 3000);
  setInterval(loadLogs, 2000);
  setInterval(updateUptime, 1000);
})();
</script>
</body>
</html>
"""

# ─── API ROUTES ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(CONTROL_PANEL_HTML)

@app.route("/api/services")
def get_services():
    return jsonify(pm.get_all_status())

@app.route("/api/services/<key>/<action>", methods=["POST"])
def service_control(key: str, action: str):
    if key not in SERVICES:
        return jsonify({"error": "Unknown service"}), 404
    
    if action == "start":
        ok = pm.start_service(key)
        return jsonify({"success": ok, "message": f"{key} started" if ok else f"{key} already running or failed"})
    elif action == "stop":
        ok = pm.stop_service(key)
        return jsonify({"success": ok, "message": f"{key} stopped" if ok else f"{key} not running"})
    elif action == "restart":
        ok = pm.restart_service(key)
        return jsonify({"success": ok, "message": f"{key} restarted"})
    else:
        return jsonify({"error": "Invalid action"}), 400

@app.route("/api/logs")
def get_logs():
    svc = request.args.get("service", "all")
    lines = int(request.args.get("lines", 50))
    if svc == "all":
        all_logs = []
        for k in SERVICES:
            all_logs.extend(pm.get_logs(k, lines))
        all_logs.sort()
        return jsonify({"logs": all_logs[-lines:]})
    return jsonify({"logs": pm.get_logs(svc, lines)})

@app.route("/api/models")
def get_models():
    return jsonify(load_model_registry())

@app.route("/api/health")
def health():
    statuses = pm.get_all_status()
    all_running = all(s["state"] == "running" for s in statuses.values())
    return jsonify({
        "status": "healthy" if all_running else "degraded",
        "services": statuses,
        "timestamp": datetime.now().isoformat()
    })

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("  KUERA UNIFIED DESKTOP v3.0")
    print("  Integrasi: KueraClaw | Kuera-AI Evolusi | Kuera API")
    print("=" * 70)
    print()
    print(f"  Control Panel: http://localhost:{CONTROL_PANEL_PORT}")
    print(f"  Working Dir  : {BASE_DIR}")
    print()
    print("  Services available:")
    for key, cfg in SERVICES.items():
        print(f"    • {cfg.name} (port {cfg.port or 'N/A'}) -> /api/services/{key}/start")
    print()
    print("  Press Ctrl+C to stop all services and exit.")
    print("=" * 70)
    print()
    
    # Initialize memory agent
    mem_agent = MemoryAgent()
    mem_agent.log_startup("KUERA Unified Desktop v3.0")
    
    pm.start_monitoring()
    
    # Auto-open browser
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{CONTROL_PANEL_PORT}")
    
    t = threading.Thread(target=open_browser, daemon=True)
    t.start()
    
    try:
        app.run(host="0.0.0.0", port=CONTROL_PANEL_PORT, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping all services...")
    finally:
        mem_agent.log_shutdown("All services stopped")
        pm.stop_all()
        print("[SHUTDOWN] All services stopped. Goodbye!")

if __name__ == "__main__":
    main()
