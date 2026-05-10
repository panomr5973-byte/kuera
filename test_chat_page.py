#!/usr/bin/env python
"""
Test script untuk memverifikasi chat interface
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("kuwera_chat.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    
    # Simple response for testing
    response_text = f"Saya menerima: '{message[:30]}...'"
    mutter = "...saya catat ini."
    
    return jsonify({
        'response': response_text,
        'mutter': mutter,
        'timestamp': datetime.now().isoformat()
    })

@app.route("/api/models")
def get_models():
    return jsonify({
        'models': [
            {'name': 'Qwen2.5-7B-Instruct', 'size_gb': 4.36},
            {'name': 'Qwen2.5-Coder-3B', 'size_gb': 1.80},
        ]
    })

if __name__ == "__main__":
    print("="*60)
    print("KUWERA AI - Test Chat Page")
    print("="*60)
    print()
    print("Buka browser dan akses: http://localhost:5001")
    print("Anda akan melihat:")
    print("  1. Header dengan logo KUWERA AI")
    print("  2. Area chat di tengah")
    print("  3. Input box di bawah untuk mengetik")
    print()
    print("Tekan Ctrl+C untuk berhenti")
    print("="*60)
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=False)
