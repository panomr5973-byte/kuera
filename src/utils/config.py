"""KUERA AI — Configuration loader.

Loads YAML configuration from config/ directory.
Provides typed access to settings and service definitions.
"""

from pathlib import Path
from typing import Any, Dict
import yaml


BASE_DIR = Path(__file__).parent.parent.parent.resolve()
CONFIG_DIR = BASE_DIR / "config"


def _load_yaml(filename: str) -> Dict[str, Any]:
    path = CONFIG_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class Settings:
    """Typed access to settings.yaml"""

    def __init__(self):
        self._data = _load_yaml("settings.yaml")

    @property
    def app_name(self) -> str:
        return self._data.get("app", {}).get("name", "KUERA")

    @property
    def app_version(self) -> str:
        return self._data.get("app", {}).get("version", "3.1")

    @property
    def debug(self) -> bool:
        return self._data.get("app", {}).get("debug", False)

    @property
    def base_dir(self) -> Path:
        return BASE_DIR

    @property
    def logs_dir(self) -> Path:
        return BASE_DIR / self._data.get("paths", {}).get("logs_dir", "logs/unified")

    @property
    def models_dir(self) -> Path:
        return BASE_DIR / self._data.get("paths", {}).get("models_dir", "models/llm")

    @property
    def data_dir(self) -> Path:
        return BASE_DIR / self._data.get("paths", {}).get("data_dir", "data")

    @property
    def memory_dir(self) -> Path:
        return BASE_DIR / self._data.get("paths", {}).get("memory_dir", "memory")

    @property
    def ports(self) -> Dict[str, int]:
        return self._data.get("ports", {})

    @property
    def control_panel_port(self) -> int:
        return self.ports.get("control_panel", 7777)

    @property
    def services_config(self) -> Dict[str, Any]:
        return self._data.get("services", {})

    @property
    def auto_start(self) -> bool:
        return self.services_config.get("auto_start", False)

    @property
    def max_restarts(self) -> int:
        return self.services_config.get("max_restarts", 5)

    @property
    def registry_file(self) -> Path:
        return BASE_DIR / self._data.get("models", {}).get("registry_file", "models/llm/model_registry_active.json")


class ServiceRegistry:
    """Typed access to services.yaml"""

    def __init__(self):
        self._data = _load_yaml("services.yaml")

    def list_services(self) -> Dict[str, Dict[str, Any]]:
        return self._data

    def get(self, key: str) -> Dict[str, Any]:
        return self._data.get(key, {})

    def keys(self):
        return self._data.keys()


# Singleton instances
settings = Settings()
registry = ServiceRegistry()
