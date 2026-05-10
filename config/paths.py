"""
Unified Path Configuration for AI Project
Manajemen path terpusat untuk workspace dual-drive (C: dan D:)
"""

import os
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class PathConfig:
    """Konfigurasi path untuk seluruh project"""
    # Drive C: - System & Active (Fast SSD)
    DRIVE_C: Path = Path("C:/AI-Project")
    
    # Drive D: - Archive & Backup (Storage)
    DRIVE_D: Path = Path("D:/")
    
    @property
    def project_root(self) -> Path:
        """Root project di C:"""
        return self.DRIVE_C
    
    @property
    def active_models(self) -> Path:
        """Model aktif yang sedang digunakan"""
        return self.DRIVE_C / "models"
    
    @property
    def database(self) -> Path:
        """Database utama (mlflow, interactions)"""
        return self.DRIVE_C / "mlflow.db"
    
    @property
    def logs(self) -> Path:
        """Log files"""
        return self.DRIVE_C / "logs"
    
    @property
    def source_code(self) -> Path:
        """Source code directory"""
        return self.DRIVE_C / "src"
    
    @property
    def self_evolving(self) -> Path:
        """Self-evolving module"""
        return self.DRIVE_C / "self_evolving"
    
    @property
    def app(self) -> Path:
        """Application directory"""
        return self.DRIVE_C / "app"
    
    @property
    def data(self) -> Path:
        """Data directory"""
        return self.DRIVE_C / "data"
    
    @property
    def training(self) -> Path:
        """Training directory"""
        return self.DRIVE_C / "training"
    
    @property
    def personal_ai(self) -> Path:
        """Personal AI directory"""
        return self.DRIVE_C / "personal_ai"
    
    # Drive D: - Archive & Backup
    @property
    def model_backup(self) -> Path:
        """Backup model di D:"""
        return self.DRIVE_D / "AI-Backup-2026/models"
    
    @property
    def model_archive(self) -> Path:
        """Archive model lama di D:"""
        return self.DRIVE_D / "AI-Models-Archive/models"
    
    @property
    def client_data(self) -> Path:
        """Data klien di D:"""
        return self.DRIVE_D / "DataKlien"
    
    @property
    def downloads(self) -> Path:
        """Downloads di D:"""
        return self.DRIVE_D / "Downloads"
    
    @property
    def archive_logs(self) -> Path:
        """Archive logs lama"""
        return self.DRIVE_D / "AI-Backup-2026/logs"
    
    def get_path(self, key: str) -> Path:
        """Get path by key name"""
        path_map = {
            # C: Drive
            "project_root": self.project_root,
            "active_models": self.active_models,
            "database": self.database,
            "logs": self.logs,
            "source_code": self.source_code,
            "self_evolving": self.self_evolving,
            "app": self.app,
            "data": self.data,
            "training": self.training,
            "personal_ai": self.personal_ai,
            
            # D: Drive
            "model_backup": self.model_backup,
            "model_archive": self.model_archive,
            "client_data": self.client_data,
            "downloads": self.downloads,
            "archive_logs": self.archive_logs,
        }
        
        if key not in path_map:
            raise KeyError(f"Path '{key}' tidak ditemukan. Available: {list(path_map.keys())}")
        
        return path_map[key]
    
    def ensure_exists(self, path: Path) -> Path:
        """Pastikan directory exists, create jika belum"""
        if path.suffix:  # It's a file (has extension)
            path.parent.mkdir(parents=True, exist_ok=True)
        else:  # It's a directory
            path.mkdir(parents=True, exist_ok=True)
        return path
    
    def list_all_paths(self) -> Dict[str, Path]:
        """List semua path yang tersedia"""
        return {
            "project_root": self.project_root,
            "active_models": self.active_models,
            "database": self.database,
            "logs": self.logs,
            "source_code": self.source_code,
            "self_evolving": self.self_evolving,
            "app": self.app,
            "data": self.data,
            "training": self.training,
            "personal_ai": self.personal_ai,
            "model_backup": self.model_backup,
            "model_archive": self.model_archive,
            "client_data": self.client_data,
            "downloads": self.downloads,
            "archive_logs": self.archive_logs,
        }


# Singleton instance
_paths = None

def get_paths() -> PathConfig:
    """Get singleton instance of PathConfig"""
    global _paths
    if _paths is None:
        _paths = PathConfig()
    return _paths


def get_path(key: str) -> Path:
    """Quick access untuk get path"""
    return get_paths().get_path(key)


def ensure_all_paths():
    """Pastikan semua path exists"""
    paths = get_paths()
    for name, path in paths.list_all_paths().items():
        paths.ensure_exists(path)
        print(f"[OK] {name}: {path}")


# Legacy compatibility - fungsi lama tetap works
def get_model_path(model_name: str) -> Path:
    """Get path untuk model tertentu"""
    return get_path("active_models") / model_name


def get_backup_path(model_name: str) -> Path:
    """Get backup path untuk model"""
    return get_path("model_backup") / model_name


if __name__ == "__main__":
    """Test paths configuration"""
    print("=" * 60)
    print("🗂️  UNIFIED PATH CONFIGURATION")
    print("=" * 60)
    
    paths = get_paths()
    
    print("\n[C: Drive - Active Workspace]")
    print("-" * 40)
    c_paths = [
        "project_root", "active_models", "database", 
        "logs", "source_code", "app", "data"
    ]
    for key in c_paths:
        path = paths.get_path(key)
        exists = "✅" if path.exists() else "⚠️"
        print(f"  [{exists}] {key}: {path}")
    
    print("\n[D: Drive - Archive & Backup]")
    print("-" * 40)
    d_paths = [
        "model_backup", "model_archive", "client_data", "downloads"
    ]
    for key in d_paths:
        path = paths.get_path(key)
        exists = "✅" if path.exists() else "⚠️"
        print(f"  {exists} {key}: {path}")
    
    print("\n" + "=" * 60)
    print("🔄 Ensuring all paths exist...")
    ensure_all_paths()
    print("=" * 60)
