#!/usr/bin/env python3
"""
Startup script for Personal AI Monitor
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from behavior_monitor_fixed import BehaviorMonitor
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    print('🚀 Starting Personal AI Behavior Monitor...')
    print('Tracks: file activity, app usage, keyboard habits')
    print('Data: logs/personal/usage.json (local only)')
    print('Stop with Ctrl+C')
    
    monitor = BehaviorMonitor(
        monitor_dirs=[
            'c:/Users/Admin/Documents',
            'c:/Users/Admin/Desktop', 
            'c:/AI-Project'
        ]
    )
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        monitor.stop()
        print('\\n✅ Monitor stopped')

