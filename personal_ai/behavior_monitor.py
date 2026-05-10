#!/usr/bin/env python3
"""
Personal Behavior Monitor - Track file usage, app activity, work habits 
for proactive AI assistance. Local-only, privacy-focused.
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
import psutil
import schedule
import keyboard
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import logging

# Setup logging
logs_dir = Path('logs/personal')
logs_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'behavior.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BehaviorMonitor')

class BehaviorMonitor:
    def __init__(self, monitor_dirs=['c:/Users/Admin/Documents', 'c:/AI-Project'], max_history_hours=24):
        self.monitor_dirs = [Path(d) for d in monitor_dirs]
        self.max_history_hours = max_history_hours
        self.activity_log = []
        self.app_usage = {}
        self.keyboard_stats = {'total_keystrokes': 0, 'apps': {}}
        self.work_patterns = {}
        
        self.observer = Observer()
        self.running = False
        
        self._load_log()
    
    def _load_log(self):
        log_file = logs_dir / 'usage.json'
        if log_file.exists():
            try:
                with open(log_file) as f:
                    data = json.load(f)
                    self.activity_log = data.get('activity', [])
                    self.app_usage = data.get('apps', {})
                    self.keyboard_stats = data.get('keyboard', self.keyboard_stats)
                logger.info(f'Loaded {len(self.activity_log)} activity records')
            except Exception as e:
                logger.error(f'Log load error: {e}')
    
    def _save_log(self):
        log_data = {
            'activity': self.activity_log[-100:],
            'apps': self.app_usage,
            'keyboard': self.keyboard_stats,
            'patterns': self._detect_patterns(),
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open(logs_dir / 'usage.json', 'w') as f:
                json.dump(log_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f'Log save error: {e}')
    
    def _detect_patterns(self):
        if len(self.activity_log) < 10:
            return {}
        
        patterns = {}
        recent = [a for a in self.activity_log if (datetime.now() - datetime.fromisoformat(a['time'])).seconds < 3600]
        
        if recent:
            hour = datetime.now().hour
            patterns['active_hour'] = hour
            patterns['frequent_files'] = {}
            for act in recent:
                if 'file' in act['type']:
                    f = act['path'].split(os.sep)[-1]
                    patterns['frequent_files'][f] = patterns['frequent_files'].get(f, 0) + 1
        
        return patterns
    
    def track_file_activity(self, event):
        if not self.running:
            return
        
        event_time = datetime.now().isoformat()
        activity = {
            'time': event_time,
            'type': 'file_access',
            'path': str(event.src_path),
            'action': event.event_type
        }
        self.activity_log.append(activity)
        logger.info(f'File: {event.src_path} {event.event_type}')
    
    def track_app_usage(self):
        if not self.running:
            return
        
        foreground_apps = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['cpu_percent'] > 0:
                    foreground_apps.append(proc.info['name'])
            except:
                pass
        
        now = datetime.now()
        app_key = '-'.join(set(foreground_apps[:3]))
        
        if app_key not in self.app_usage:
            self.app_usage[app_key] = []
        
        self.app_usage[app_key].append(now.isoformat())
        
        cutoff = now - timedelta(hours=self.max_history_hours)
        self.app_usage[app_key] = [t for t in self.app_usage[app_key] if datetime.fromisoformat(t) > cutoff]
    
    def track_keyboard(self, event):
        if not self.running:
            return
        
        self.keyboard_stats['total_keystrokes'] += 1
        try:
            app = psutil.Process().name()
            self.keyboard_stats['apps'][app] = self.keyboard_stats['apps'].get(app, 0) + 1
        except:
            pass
    
    def start_file_watcher(self):
        class Handler(FileSystemEventHandler):
            def on_any(self, event):
                self.track_file_activity(event)
        
        handler = Handler()
        
        for monitor_dir in self.monitor_dirs:
            if monitor_dir.exists():
                self.observer.schedule(handler, str(monitor_dir), recursive=True)
                logger.info(f'Watching {monitor_dir}')
        
        self.observer.start()
    
    def start(self):
        self.running = True
        logger.info('Starting Behavior Monitor...')
        
        threading.Thread(target=self.start_file_watcher, daemon=True).start()
        
        schedule.every(30).seconds.do(self.track_app_usage)
        keyboard.on_press(self.track_keyboard)
        schedule.every(5).minutes.do(self._save_log)
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        self.running = False
        self.observer.stop()
        self.observer.join()
        keyboard.unhook_all()
        self._save_log()
        logger.info('Behavior Monitor stopped')

if __name__ == '__main__':
    monitor = BehaviorMonitor()
    try:
        monitor.start()
    except KeyboardInterrupt:
        monitor.stop()

