#!/usr/bin/env python3
"""
Start Dashboard Script
======================
Script untuk menjalankan Streamlit dashboard tanpa prompt email.
"""

import subprocess
import os
import sys

def start_dashboard():
    """Start Streamlit dashboard"""
    
    # Set environment variable untuk skip email prompt
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    
    # Create streamlit config untuk menghindari prompt
    config_dir = os.path.expanduser('~/.streamlit')
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, 'config.toml')
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            f.write("""[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501
""")
    
    print("="*60)
    print("STARTING STREAMLIT DASHBOARD")
    print("="*60)
    print()
    print("🚀 Dashboard URL: http://localhost:8501")
    print("📊 Dashboard akan terbuka otomatis di browser")
    print()
    print("Tekan Ctrl+C untuk berhenti")
    print("="*60)
    print()
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "app/dashboard.py",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard stopped")

if __name__ == "__main__":
    start_dashboard()
