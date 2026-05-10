"""
Daily Maintenance Script
Jalankan script ini setiap hari untuk maintenance otomatis:
1. Sync models C: -> D:
2. Check disk space
3. Archive old logs
4. Generate reports
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.paths import get_paths, ensure_all_paths


def run_sync():
    """Run model sync"""
    print("\n" + "="*60)
    print("[STEP 1] MODEL SYNC")
    print("="*60)
    
    try:
        from scripts.sync_models import ModelSync
        sync = ModelSync()
        result = sync.run_full_sync(archive_old=False)
        return True
    except Exception as e:
        print(f"[ERROR] Sync failed: {e}")
        return False


def run_monitoring():
    """Run disk monitoring"""
    print("\n" + "="*60)
    print("[STEP 2] DISK MONITORING")
    print("="*60)
    
    try:
        from monitoring.disk_monitor import DiskMonitor
        monitor = DiskMonitor()
        report, alerts = monitor.run(save_html=True)
        
        # Return True jika tidak ada critical alerts
        critical_alerts = [a for a in alerts if a["level"] == "CRITICAL"]
        return len(critical_alerts) == 0
    except Exception as e:
        print(f"[ERROR] Monitoring failed: {e}")
        return False


def archive_old_logs(days: int = 30):
    """Archive logs older than N days"""
    print("\n" + "="*60)
    print(f"[STEP 3] ARCHIVE OLD LOGS ({days} days)")
    print("="*60)
    
    import shutil
    
    paths = get_paths()
    log_dir = paths.logs
    archive_dir = paths.archive_logs
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    cutoff = datetime.now().timestamp() - (days * 24 * 3600)
    archived = 0
    
    for log_file in log_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff:
            try:
                target = archive_dir / log_file.name
                shutil.move(str(log_file), str(target))
                archived += 1
                print(f"  [ARCHIVED] {log_file.name}")
            except Exception as e:
                print(f"  [ERROR] {log_file.name}: {e}")
    
    print(f"  Total archived: {archived} files")
    return True


def generate_summary():
    """Generate daily summary"""
    print("\n" + "="*60)
    print("[STEP 4] DAILY SUMMARY")
    print("="*60)
    
    paths = get_paths()
    
    # Count models
    active_models = list(paths.active_models.glob("*.pkl"))
    backup_models = list(paths.model_backup.glob("*.pkl"))
    
    print(f"  Active models: {len(active_models)}")
    print(f"  Backup models: {len(backup_models)}")
    print(f"  Last sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check synced
    synced = len(set(m.name for m in active_models) & set(m.name for m in backup_models))
    print(f"  Synced: {synced}/{len(active_models)}")
    
    return True


def main():
    """Main maintenance routine"""
    print("="*60)
    print("[DAILY MAINTENANCE - AI PROJECT]")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Ensure all paths exist
    print("\n[INIT] Ensuring all paths exist...")
    ensure_all_paths()
    
    results = {
        "sync": run_sync(),
        "monitoring": run_monitoring(),
        "archive_logs": archive_old_logs(),
        "summary": generate_summary()
    }
    
    # Final summary
    print("\n" + "="*60)
    print("[MAINTENANCE COMPLETE]")
    print("="*60)
    
    all_ok = all(results.values())
    
    for task, success in results.items():
        status = "[OK]" if success else "[FAILED]"
        print(f"  {status} {task}")
    
    print(f"\nOverall: {'[SUCCESS]' if all_ok else '[WARNINGS]'}")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return all_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
