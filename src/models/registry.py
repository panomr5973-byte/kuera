"""KUERA AI — Model Registry Loader.

Loads and validates the active model registry JSON.
"""

import json
from pathlib import Path
from typing import Dict, Any

from ..utils.config import settings


def load_model_registry() -> Dict[str, Any]:
    """Load model registry from configured path."""
    reg_path = settings.registry_file
    if reg_path.exists():
        try:
            with open(reg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"models": [], "total_models": 0, "total_size_gb": 0, "error": str(e)}
    return {"models": [], "total_models": 0, "total_size_gb": 0}
