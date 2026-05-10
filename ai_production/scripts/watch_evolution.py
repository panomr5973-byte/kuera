import time
import os
import subprocess
import sys
import json

def run_evolution_check():
    result = subprocess.run(['python', 'check_evolution.py'], capture_output=True, text=True, cwd='.')
    print(result.stdout)
    return result.stdout

print("🚀 Starting AI Evolution Monitor...")
print("Press Ctrl+C to stop. Live updates every 60s.")

try:
    while True:
        print("\n" + "="*80)
        print(f"[LIVE UPDATE] {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        run_evolution_check()
        print("\n⏳ Waiting 60s for next update...")
        time.sleep(60)
except KeyboardInterrupt:
    print("\n👋 Monitor stopped.")
