#!/usr/bin/env python3
"""Launcher for KUERA Canonical API (v3.0)

Run: python start_api.py
"""
import subprocess
import sys

if __name__ == "__main__":
    print("=" * 60)
    print("Starting KUERA AI API v3.0")
    print("=" * 60)
    print("Docs:     http://localhost:8000/docs")
    print("Health:   http://localhost:8000/health")
    print("Models:   http://localhost:8000/models")
    print("=" * 60)
    
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "src.web.api:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload", "false"
    ])
