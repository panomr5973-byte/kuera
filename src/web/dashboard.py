"""KUERA AI — Flask Dashboard.

Serves the control panel UI and REST API routes.
HTML template is loaded from src/web/templates/control_panel.html
"""

import json
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS

from ..utils.config import settings
from ..utils.logger import setup_logger

logger = setup_logger("KUERA-Dashboard")

# Load HTML template from file
TEMPLATE_PATH = Path(__file__).parent / "templates" / "control_panel.html"
CONTROL_PANEL_HTML = TEMPLATE_PATH.read_text(encoding="utf-8")


def create_app(process_manager, model_registry_loader) -> Flask:
    """Create and configure Flask app with routes."""
    app = Flask(__name__)
    CORS(app)
    pm = process_manager
    load_registry = model_registry_loader

    @app.route("/")
    def index():
        return render_template_string(CONTROL_PANEL_HTML)

    @app.route("/api/services")
    def get_services():
        return jsonify(pm.get_all_status())

    @app.route("/api/services/<key>/<action>", methods=["POST"])
    def service_control(key: str, action: str):
        if key not in pm.services:
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
            for k in pm.services:
                all_logs.extend(pm.get_logs(k, lines))
            all_logs.sort()
            return jsonify({"logs": all_logs[-lines:]})
        return jsonify({"logs": pm.get_logs(svc, lines)})

    @app.route("/api/models")
    def get_models():
        return jsonify(load_registry())

    @app.route("/api/health")
    def health():
        statuses = pm.get_all_status()
        all_running = all(s["state"] == "running" for s in statuses.values())
        from datetime import datetime
        return jsonify({
            "status": "healthy" if all_running else "degraded",
            "services": statuses,
            "timestamp": datetime.now().isoformat()
        })

    # ─── AUDIT TOOLKIT ROUTES ────────────────────────────────────────────
    @app.route("/api/audit/files")
    def audit_files():
        from ..data.audit_connector import list_uploaded_files
        return jsonify({"files": list_uploaded_files()})

    @app.route("/api/audit/analyze", methods=["POST"])
    def audit_analyze():
        from ..data.audit_connector import analyze_excel
        data = request.get_json() or {}
        filepath = data.get("filepath", "")
        if not filepath:
            return jsonify({"status": "error", "message": "filepath required"}), 400
        result = analyze_excel(filepath)
        return jsonify(result)

    # ─── WORLDBANK ROUTES ────────────────────────────────────────────────
    @app.route("/api/economy/indonesia")
    def economy_indonesia():
        from ..data.worldbank_connector import get_latest_economic_data
        return jsonify(get_latest_economic_data())

    @app.route("/api/economy/indicators")
    def economy_indicators():
        from ..data.worldbank_connector import get_indicators_list
        return jsonify(get_indicators_list())

    @app.route("/api/economy/historical")
    def economy_historical():
        from ..data.worldbank_connector import get_historical_data
        code = request.args.get("code", "")
        years = int(request.args.get("years", 10))
        if not code:
            return jsonify({"status": "error", "message": "code parameter required"}), 400
        return jsonify(get_historical_data(code, years))

    return app


def run_dashboard(process_manager, model_registry_loader, port: int = None, open_browser: bool = True):
    """Run the dashboard server."""
    port = port or settings.control_panel_port
    app = create_app(process_manager, model_registry_loader)

    if open_browser:
        import threading
        import webbrowser
        import time

        def _open():
            time.sleep(1.5)
            webbrowser.open(f"http://localhost:{port}")

        threading.Thread(target=_open, daemon=True).start()

    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
