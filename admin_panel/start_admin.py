"""
Start KUWERA Admin Panel
Script untuk menjalankan admin panel dengan mudah
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def main():
    print("="*60)
    print("[KUWERA Admin Panel Launcher]")
    print("="*60)
    print()
    
    # Check if Flask is installed
    try:
        import flask
        import flask_cors
    except ImportError:
        print("[INFO] Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors", "-q"])
        print("[OK] Packages installed")
    
    # Start server
    print("[START] Starting Admin Panel Server...")
    print()
    
    # Open browser after delay
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask server
    api_dir = Path(__file__).parent / "api"
    server_script = api_dir / "server.py"
    
    try:
        subprocess.run([sys.executable, str(server_script)])
    except KeyboardInterrupt:
        print()
        print("[STOP] Server stopped")

if __name__ == '__main__':
    main()
