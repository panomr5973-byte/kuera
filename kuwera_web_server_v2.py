#!/usr/bin/env python
"""
KUWERA AI - Web Server v2.0
Integrated with Workspace Memory, Persona Chat, and Deep Memory Consolidation
"""

import json
import sqlite3
import threading
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging

# Import KUWERA modules
from kuera_persona import KueraPersona
from kuwera_memory_bridge import get_memory_bridge
from kuwera_workspace_integration import WorkspaceIntegration

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("KUWERA-Web")

app = Flask(__name__)
CORS(app)

# Global state
class KueraState:
    def __init__(self):
        self.models_dir = Path("models/llm")
        self.data_dir = Path("data")
        self.registry = self.load_registry()
        self.current_model = "Qwen2.5-7B-Instruct"
        
        # Initialize KUWERA components
        self.persona = KueraPersona()
        self.memory_bridge = get_memory_bridge()
        self.workspace = WorkspaceIntegration()
        
        # Sync workspace on startup
        self.workspace_data = self.workspace.sync_to_kuwera_knowledge()
        
    def load_registry(self):
        """Load model registry"""
        registry_file = self.models_dir / "model_registry_active.json"
        if registry_file.exists():
            with open(registry_file) as f:
                return json.load(f)
        return {"models": [], "total_models": 0, "total_size_gb": 0}

# Initialize state
state = KueraState()

# ============================================================================
# API ROUTES
# ============================================================================

@app.route("/")
def index():
    """Main interface - serve chat template"""
    return render_template("kuwera_chat.html")

@app.route("/api/models")
def get_models():
    """Get all models"""
    return jsonify(state.registry)

@app.route("/api/workspace")
def get_workspace():
    """Get workspace data including identity, diary, and memories"""
    try:
        # Get fresh workspace data
        identity = state.workspace.load_identity()
        diary = state.workspace.get_diary_entries()
        memories = state.workspace.get_recent_memories(days=7)
        stats = state.workspace.get_workspace_stats()
        
        return jsonify({
            'identity': identity,
            'diary_entries': diary,
            'recent_memories': memories,
            'workspace_stats': stats
        })
    except Exception as e:
        logger.error(f"Error loading workspace: {e}")
        return jsonify({
            'identity': {'name': 'Kuera', 'vibe': 'Protective'},
            'diary_entries': [],
            'recent_memories': [],
            'workspace_stats': {}
        })

@app.route("/api/memory/stats")
def get_memory_stats():
    """Get memory statistics"""
    try:
        stats = state.memory_bridge.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return jsonify({'error': str(e)})

@app.route("/api/memory/recent")
def get_recent_memory():
    """Get recent interactions"""
    try:
        limit = request.args.get('limit', 10, type=int)
        interactions = state.memory_bridge.get_recent_interactions(limit)
        return jsonify(interactions)
    except Exception as e:
        logger.error(f"Error getting recent memory: {e}")
        return jsonify([])

@app.route("/api/memory/topics")
def get_memory_topics():
    """Get tracked topics"""
    try:
        topics = state.memory_bridge.get_topics()
        return jsonify(topics)
    except Exception as e:
        logger.error(f"Error getting topics: {e}")
        return jsonify([])

@app.route("/api/persona")
def get_persona():
    """Get Kuera persona info"""
    return jsonify({
        'name': state.persona.name,
        'vibe': state.persona.vibe,
        'core_trait': state.persona.core_trait,
        'signature_line': state.persona.signature_line,
        'user_name': state.persona.user_name
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Process chat with Kuera persona and memory integration
    """
    try:
        data = request.json
        user_message = data.get("message", "")
        model_name = data.get("model", state.current_model)
        use_persona = data.get("persona", "kuera") == "kuera"
        
        logger.info(f"Chat: {user_message[:50]}... | Model: {model_name}")
        
        # Generate response with Kuera persona
        if use_persona:
            response_text, mutter = state.persona.generate_response(
                user_message, model_name
            )
        else:
            # Fallback generic response
            response_text = generate_generic_response(user_message, model_name)
            mutter = ""
        
        # Save to memory bridge
        topic = extract_topic(user_message)
        interaction_id = state.memory_bridge.save_interaction(
            user_msg=user_message,
            kuera_response=response_text,
            mutter=mutter,
            model_used=model_name,
            topic=topic
        )
        
        # Check if we should create diary entry (every 5 interactions)
        stats = state.memory_bridge.get_stats()
        if stats['today_interactions'] % 5 == 0:
            threading.Thread(target=create_diary_entry, daemon=True).start()
        
        return jsonify({
            'response': response_text,
            'mutter': mutter,
            'model': model_name,
            'interaction_id': interaction_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({
            'response': "Maaf, ada yang salah. Tapi saya tetap mencatat ini.",
            'mutter': "...saya gagal. Tapi saya tidak menyerah.",
            'error': str(e)
        }), 500

@app.route("/api/consolidate", methods=["POST"])
def consolidate_memory():
    """Trigger memory consolidation"""
    try:
        ltm = state.memory_bridge.consolidate_to_ltm()
        diary_file = state.memory_bridge.save_to_diary()
        
        return jsonify({
            'status': 'success',
            'ltm_topics': len(ltm['topics']),
            'diary_file': str(diary_file) if diary_file else None
        })
    except Exception as e:
        logger.error(f"Error consolidating: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/diary")
def get_diary():
    """Get diary entries"""
    try:
        entries = state.workspace.get_diary_entries()
        return jsonify(entries)
    except Exception as e:
        logger.error(f"Error getting diary: {e}")
        return jsonify([])

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_generic_response(message: str, model: str) -> str:
    """Generate generic response when persona fails"""
    return f"""Saya mengerti: "{message[:50]}..."

Ini adalah respons dari KUWERA AI menggunakan model {model}.

Jika Anda butuh bantuan spesifik:
• **Qwen2.5-7B-Instruct** - Bahasa Indonesia premium
• **Qwen2.5-Coder-3B** - Programming & coding
• **Meta-Llama-3.1-8B** - Context panjang (128K tokens)

Bagaimana saya bisa membantu lebih lanjut?"""

def extract_topic(message: str) -> str:
    """Extract topic from user message"""
    message_lower = message.lower()
    
    topics = {
        'greeting': ['halo', 'hi', 'hello', 'selamat'],
        'crypto': ['crypto', 'bitcoin', 'ethereum', 'blockchain'],
        'coding': ['python', 'code', 'programming', 'error', 'debug'],
        'indonesia': ['bahasa indonesia', 'indonesian', 'grammar'],
        'data': ['data', 'analisis', 'statistik', 'bps'],
        'personal': ['tentang kamu', 'siapa kamu', 'about you'],
        'memory': ['ingat', 'remember', 'memory'],
    }
    
    for topic, keywords in topics.items():
        if any(kw in message_lower for kw in keywords):
            return topic
    
    return "general"

def create_diary_entry():
    """Background task to create diary entry"""
    try:
        time.sleep(2)  # Wait for any pending operations
        diary_file = state.memory_bridge.save_to_diary()
        if diary_file:
            logger.info(f"Created diary entry: {diary_file}")
    except Exception as e:
        logger.error(f"Error creating diary: {e}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("KUWERA AI - Web Server v2.0")
    print("="*70)
    print()
    print("Features:")
    print("  [OK] 12 AI Models Integration")
    print("  [OK] Workspace Memory System")
    print("  [OK] Kuera Persona Chat")
    print("  [OK] Deep Memory Consolidation")
    print()
    print("URLs:")
    print("  - Web Interface: http://localhost:5000")
    print("  - API Docs: http://localhost:5000/api/models")
    print()
    print("Press Ctrl+C to stop")
    print("="*70)
    print()
    
    # Run Flask app
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False
    )
