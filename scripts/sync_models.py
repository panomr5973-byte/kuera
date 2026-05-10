"""
Auto-Sync Script for Model Backup
Sinkronisasi model dari C: ke D: secara otomatis
"""

import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
import sys
import json

# Add parent to path untuk import config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.paths import get_paths, get_path


class ModelSync:
    """Manager untuk sync model antara C: dan D:"""
    
    def __init__(self):
        self.paths = get_paths()
        self.source = self.paths.active_models
        self.backup = self.paths.model_backup
        self.archive = self.paths.model_archive
        self.log_file = self.paths.logs / "sync_history.json"
        
        # Ensure directories exist
        self.backup.mkdir(parents=True, exist_ok=True)
        self.archive.mkdir(parents=True, exist_ok=True)
        
    def get_file_hash(self, filepath: Path) -> str:
        """Get MD5 hash dari file untuk comparison"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def needs_sync(self, source_file: Path, target_file: Path) -> bool:
        """Cek apakah file perlu di-sync"""
        if not target_file.exists():
            return True
        
        # Compare modification time
        source_mtime = source_file.stat().st_mtime
        target_mtime = target_file.stat().st_mtime
        
        if source_mtime > target_mtime:
            return True
        
        # Compare size
        if source_file.stat().st_size != target_file.stat().st_size:
            return True
            
        return False
    
    def sync_file(self, source: Path, target: Path) -> dict:
        """Sync single file dengan logging"""
        result = {
            "source": str(source),
            "target": str(target),
            "status": "skipped",
            "timestamp": datetime.now().isoformat(),
            "size_bytes": 0
        }
        
        try:
            if self.needs_sync(source, target):
                # Backup existing file jika ada
                if target.exists():
                    backup_name = f"{target.stem}_old_{datetime.now().strftime('%Y%m%d')}{target.suffix}"
                    backup_path = target.parent / backup_name
                    shutil.move(target, backup_path)
                
                # Copy file baru
                shutil.copy2(source, target)
                
                result["status"] = "synced"
                result["size_bytes"] = target.stat().st_size
                print(f"  [OK] Synced: {source.name} ({result['size_bytes'] / 1024 / 1024:.2f} MB)")
            else:
                print(f"  [SKIP] Skipped: {source.name} (up-to-date)")
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"  [ERROR] {source.name} - {e}")
        
        return result
    
    def sync_models(self, pattern: str = "*.pkl") -> List[dict]:
        """Sync semua model files"""
        print(f"\n[SYNC] Syncing models from {self.source} to {self.backup}")
        print("-" * 60)
        
        results = []
        model_files = list(self.source.glob(pattern))
        
        if not model_files:
            print("  ⚠️  No model files found")
            return results
        
        for source_file in model_files:
            target_file = self.backup / source_file.name
            result = self.sync_file(source_file, target_file)
            results.append(result)
        
        return results
    
    def sync_registry_files(self) -> List[dict]:
        """Sync registry dan metadata files"""
        print(f"\n[SYNC] Syncing registry files")
        print("-" * 60)
        
        results = []
        registry_files = [
            "model_registry.json",
            "model_registry_fixed.json",
            "model_metadata.json",
            "hf_registry.json"
        ]
        
        for filename in registry_files:
            source_file = self.source / filename
            if source_file.exists():
                target_file = self.backup / filename
                result = self.sync_file(source_file, target_file)
                results.append(result)
        
        return results
    
    def archive_old_models(self, days_old: int = 30) -> List[dict]:
        """Pindahkan model lama ke archive"""
        print(f"\n[ARCHIVE] Archiving models older than {days_old} days")
        print("-" * 60)
        
        results = []
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 3600)
        
        for model_file in self.source.glob("*.pkl"):
            # Skip best models dan latest models
            if "best" in model_file.name.lower():
                continue
                
            file_mtime = model_file.stat().st_mtime
            if file_mtime < cutoff_date:
                archive_file = self.archive / model_file.name
                
                try:
                    shutil.move(str(model_file), str(archive_file))
                    results.append({
                        "file": model_file.name,
                        "status": "archived",
                        "target": str(archive_file)
                    })
                    print(f"  [ARCHIVED] {model_file.name}")
                except Exception as e:
                    results.append({
                        "file": model_file.name,
                        "status": "error",
                        "error": str(e)
                    })
                    print(f"  [ERROR] Archiving {model_file.name} - {e}")
        
        return results
    
    def verify_backup(self) -> dict:
        """Verifikasi integritas backup"""
        print(f"\n[VERIFY] Verifying backup integrity")
        print("-" * 60)
        
        report = {
            "source_count": 0,
            "backup_count": 0,
            "synced_count": 0,
            "missing_files": [],
            "timestamp": datetime.now().isoformat()
        }
        
        source_models = set(f.name for f in self.source.glob("*.pkl"))
        backup_models = set(f.name for f in self.backup.glob("*.pkl"))
        
        report["source_count"] = len(source_models)
        report["backup_count"] = len(backup_models)
        report["synced_count"] = len(source_models & backup_models)
        report["missing_files"] = list(source_models - backup_models)
        
        print(f"  Source models: {report['source_count']}")
        print(f"  Backup models: {report['backup_count']}")
        print(f"  Synced: {report['synced_count']}")
        
        if report["missing_files"]:
            print(f"  [WARNING] Missing in backup: {report['missing_files']}")
        
        return report
    
    def save_log(self, results: dict):
        """Save sync log ke file"""
        logs = []
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "results": results
        })
        
        # Keep only last 100 logs
        logs = logs[-100:]
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def run_full_sync(self, archive_old: bool = False):
        """Jalankan full sync process"""
        print("=" * 60)
        print("[MODEL SYNC SERVICE]")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        all_results = {
            "models": [],
            "registry": [],
            "archive": [],
            "verification": {}
        }
        
        # 1. Sync models
        all_results["models"] = self.sync_models("*.pkl")
        
        # 2. Sync joblib files
        all_results["models"].extend(self.sync_models("*.joblib"))
        
        # 3. Sync registry files
        all_results["registry"] = self.sync_registry_files()
        
        # 4. Archive old models jika diminta
        if archive_old:
            all_results["archive"] = self.archive_old_models()
        
        # 5. Verify backup
        all_results["verification"] = self.verify_backup()
        
        # 6. Save log
        self.save_log(all_results)
        
        # Summary
        print("\n" + "=" * 60)
        print("[SYNC SUMMARY]")
        print("=" * 60)
        
        synced = sum(1 for r in all_results["models"] if r.get("status") == "synced")
        skipped = sum(1 for r in all_results["models"] if r.get("status") == "skipped")
        errors = sum(1 for r in all_results["models"] if r.get("status") == "error")
        
        print(f"  Synced: {synced} files")
        print(f"  Skipped: {skipped} files")
        print(f"  Errors: {errors} files")
        print(f"  Total size: {sum(r.get('size_bytes', 0) for r in all_results['models']) / 1024 / 1024:.2f} MB")
        
        print("=" * 60)
        
        return all_results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Model Sync Service")
    parser.add_argument("--archive", action="store_true", help="Archive old models")
    parser.add_argument("--verify", action="store_true", help="Verify backup only")
    
    args = parser.parse_args()
    
    sync = ModelSync()
    
    if args.verify:
        sync.verify_backup()
    else:
        sync.run_full_sync(archive_old=args.archive)


if __name__ == "__main__":
    main()
