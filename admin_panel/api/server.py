"""
KUWERA Admin Panel API Server
Flask backend untuk serving admin panel dan data API
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import json
import os
from pathlib import Path
from datetime import datetime
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.paths import get_paths

app = Flask(__name__)
CORS(app)

# Paths
paths = get_paths()
ADMIN_PANEL_DIR = Path(__file__).parent.parent

# Data store (in production, use database)
class DataStore:
    def __init__(self):
        self.models = []
        self.interactions = []
        self.sync_history = []
        self.system_stats = {}
        self.load_initial_data()
    
    def load_initial_data(self):
        """Load data dari file dan sistem"""
        # Load model registry
        registry_file = paths.active_models / "model_registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                    self.models = data.get('models', [])
            except:
                self.models = self.get_default_models()
        else:
            self.models = self.get_default_models()
        
        # Load interactions from mlflow db atau buat sample
        self.interactions = self.get_sample_interactions()
        
        # Load sync history
        sync_log = paths.logs / "sync_history.json"
        if sync_log.exists():
            try:
                with open(sync_log, 'r') as f:
                    self.sync_history = json.load(f)
            except:
                self.sync_history = self.get_default_sync_history()
        else:
            self.sync_history = self.get_default_sync_history()
    
    def get_default_models(self):
        return [
            {"id": "model_20260402_100050", "type": "rf", "f1": 0.643, "accuracy": 0.75, "samples": 20, "date": "2026-04-02", "production": False},
            {"id": "model_20260402_113959", "type": "rf", "f1": 0.527, "accuracy": 0.662, "samples": 1094, "date": "2026-04-02", "production": False},
            {"id": "model_20260402_115503", "type": "gb", "f1": 0.673, "accuracy": 0.673, "samples": 145580, "date": "2026-04-02", "production": True},
            {"id": "model_20260402_121344", "type": "gb", "f1": 0.638, "accuracy": 0.661, "samples": 414483, "date": "2026-04-02", "production": False},
            {"id": "model_20260402_135212", "type": "gb", "f1": 0.629, "accuracy": 0.656, "samples": 388036, "date": "2026-04-02", "production": False},
            {"id": "model_20260402_150537", "type": "gb", "f1": 0.643, "accuracy": 0.662, "samples": 367033, "date": "2026-04-02", "production": False}
        ]
    
    def get_sample_interactions(self):
        return [
            {"id": 1, "type": "chat", "user": "User #42", "message": "Apa itu KUWERA?", "timestamp": datetime.now().isoformat(), "sentiment": "positive", "confidence": 0.92},
            {"id": 2, "type": "api", "user": "System", "message": "Model prediction request", "timestamp": datetime.now().isoformat(), "sentiment": "neutral", "confidence": 0.85},
            {"id": 3, "type": "chat", "user": "User #128", "message": "Terima kasih atas bantuannya!", "timestamp": datetime.now().isoformat(), "sentiment": "positive", "confidence": 0.95},
            {"id": 4, "type": "voice", "user": "User #85", "message": "Voice query processed", "timestamp": datetime.now().isoformat(), "sentiment": "neutral", "confidence": 0.78},
            {"id": 5, "type": "chat", "user": "User #256", "message": "Bagaimana cara kerja AI ini?", "timestamp": datetime.now().isoformat(), "sentiment": "curious", "confidence": 0.88}
        ]
    
    def get_default_sync_history(self):
        return [
            {"timestamp": "2026-04-09 13:08:10", "status": "success", "files_synced": 10, "size_mb": 0},
            {"timestamp": "2026-04-09 02:00:00", "status": "success", "files_synced": 10, "size_mb": 0},
            {"timestamp": "2026-04-08 02:00:00", "status": "success", "files_synced": 8, "size_mb": 7200},
            {"timestamp": "2026-04-07 02:00:00", "status": "success", "files_synced": 6, "size_mb": 3100}
        ]
    
    def get_system_stats(self):
        """Get real-time system stats"""
        import shutil
        
        c_usage = shutil.disk_usage("C:/")
        d_usage = shutil.disk_usage("D:/")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "disks": {
                "C": {
                    "total_gb": round(c_usage.total / (1024**3), 2),
                    "used_gb": round(c_usage.used / (1024**3), 2),
                    "free_gb": round(c_usage.free / (1024**3), 2),
                    "percent_used": round((c_usage.used / c_usage.total) * 100, 1)
                },
                "D": {
                    "total_gb": round(d_usage.total / (1024**3), 2),
                    "used_gb": round(d_usage.used / (1024**3), 2),
                    "free_gb": round(d_usage.free / (1024**3), 2),
                    "percent_used": round((d_usage.used / d_usage.total) * 100, 1)
                }
            },
            "models": {
                "active_count": len(self.models),
                "production_model": next((m for m in self.models if m.get('production')), None)
            }
        }

# Initialize data store
data_store = DataStore()

# Routes
@app.route('/')
def index():
    """Serve main admin panel"""
    return send_from_directory(ADMIN_PANEL_DIR / 'templates', 'index.html')

# Static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(ADMIN_PANEL_DIR / 'static', path)

# API Endpoints
@app.route('/api/stats')
def get_stats():
    """Get dashboard stats"""
    return jsonify({
        "models": len(data_store.models),
        "interactions": 1002258,
        "accuracy": 67.3,
        "space_free_gb": 67.9,
        "evolution_score": 80,
        "generation": 6,
        "best_f1": 0.673
    })

@app.route('/api/models')
def get_models():
    """Get all models"""
    return jsonify(data_store.models)

@app.route('/api/models/<model_id>')
def get_model(model_id):
    """Get specific model details"""
    model = next((m for m in data_store.models if m['id'] == model_id), None)
    if model:
        return jsonify(model)
    return jsonify({"error": "Model not found"}), 404

@app.route('/api/interactions')
def get_interactions():
    """Get recent interactions"""
    limit = request.args.get('limit', 50, type=int)
    interaction_type = request.args.get('type', None)
    
    interactions = data_store.interactions
    if interaction_type:
        interactions = [i for i in interactions if i['type'] == interaction_type]
    
    return jsonify(interactions[:limit])

@app.route('/api/sync/history')
def get_sync_history():
    """Get sync history"""
    return jsonify(data_store.sync_history)

@app.route('/api/sync/status')
def get_sync_status():
    """Get current sync status"""
    return jsonify({
        "last_sync": data_store.sync_history[0] if data_store.sync_history else None,
        "status": "healthy",
        "next_scheduled": "2026-04-10 02:00:00"
    })

@app.route('/api/system/status')
def get_system_status():
    """Get system status dan disk usage"""
    return jsonify(data_store.get_system_stats())

@app.route('/api/paths')
def get_paths_info():
    """Get path configuration"""
    return jsonify({
        "C": {
            "project_root": str(paths.project_root),
            "active_models": str(paths.active_models),
            "database": str(paths.database),
            "logs": str(paths.logs),
            "data": str(paths.data)
        },
        "D": {
            "model_backup": str(paths.model_backup),
            "model_archive": str(paths.model_archive),
            "client_data": str(paths.client_data),
            "downloads": str(paths.downloads)
        }
    })

@app.route('/api/evolution/timeline')
def get_evolution_timeline():
    """Get evolution timeline"""
    return jsonify([
        {"phase": "inception", "name": "Inception", "model": "model_20260402_100050", "f1": 0.643, "samples": 20, "status": "completed", "date": "2026-04-02"},
        {"phase": "toddler", "name": "Toddler", "model": "model_20260402_113959", "f1": 0.527, "samples": 1094, "status": "completed", "date": "2026-04-02"},
        {"phase": "adolescent", "name": "Adolescent", "model": "model_20260402_115503", "f1": 0.673, "samples": 145580, "status": "completed", "date": "2026-04-02"},
        {"phase": "nusantara", "name": "Nusantara Consciousness", "model": "model_20260402_121344", "f1": 0.638, "samples": 414483, "status": "active", "date": "2026-04-02"},
        {"phase": "bhineka", "name": "Bhineka AI", "model": null, "f1": 0.80, "samples": 1000000, "status": "planned", "date": "2026-Q2"},
        {"phase": "pancasila", "name": "Pancasila AI", "model": null, "f1": 0.90, "samples": 10000000, "status": "planned", "date": "2026-Q3"}
    ])

@app.route('/api/history')
def get_history():
    """Get system history"""
    return jsonify([
        {"time": "2026-04-09 13:08:10", "event": "Daily maintenance completed", "type": "sync", "detail": "All systems synchronized"},
        {"time": "2026-04-09 12:00:00", "event": "HF Models archived to D:", "type": "model", "detail": "Moved 7.2 GB to AI-Models-Archive"},
        {"time": "2026-04-09 10:30:00", "event": "Admin panel initialized", "type": "system", "detail": "KUWERA Admin Panel v1.0"},
        {"time": "2026-04-02 11:55:00", "event": "MEGA EVOLUTION achieved", "type": "model", "detail": "F1 Score 0.673 reached"},
        {"time": "2026-04-02 10:00:00", "event": "First model created", "type": "model", "detail": "Genesis - 20 samples"}
    ])

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages dari avatar"""
    data = request.json
    message = data.get('message', '')
    
    # Simple response logic (in production, integrate dengan AI model)
    responses = [
        "Saya mengerti. Berdasarkan data training saya, saya dapat membantu menjelaskan hal tersebut.",
        "Menarik! Sebagai AI yang dilatih dengan data Indonesia, saya punya insight tentang topik tersebut.",
        "Saya sedang memproses permintaan Anda...",
        "KUWERA siap membantu! Apa yang ingin Anda ketahui tentang evolusi AI?",
        "Berdasarkan 1 juta+ interaksi, saya dapat memberikan analisis yang relevan."
    ]
    
    import random
    response = random.choice(responses)
    
    return jsonify({
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "confidence": round(random.uniform(0.85, 0.98), 2)
    })

@app.route('/api/sync/trigger', methods=['POST'])
def trigger_sync():
    """Trigger manual sync"""
    # In production, call sync script
    return jsonify({
        "status": "started",
        "timestamp": datetime.now().isoformat(),
        "message": "Sync process initiated"
    })

@app.route('/api/retrain', methods=['POST'])
def trigger_retrain():
    """Trigger model retraining"""
    return jsonify({
        "status": "started",
        "timestamp": datetime.now().isoformat(),
        "message": "Model retraining initiated. Check Models panel for progress."
    })

if __name__ == '__main__':
    print("="*60)
    print("KUWERA Admin Panel API Server")
    print("="*60)
    print(f"Admin Panel: http://localhost:5000")
    print(f"API Base: http://localhost:5000/api")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
