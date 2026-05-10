"""
Config module for AI Project
"""
from .paths import (
    PathConfig,
    get_paths,
    get_path,
    ensure_all_paths,
    get_model_path,
    get_backup_path,
)

__all__ = [
    "PathConfig",
    "get_paths",
    "get_path",
    "ensure_all_paths",
    "get_model_path",
    "get_backup_path",
]
