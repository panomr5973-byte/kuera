"""KUERA AI — Service registry loader.

Reads service definitions from config/services.yaml and provides
typed dataclass access.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

from ..utils.config import BASE_DIR
from ..utils.config import registry as _registry


@dataclass
class ServiceConfig:
    name: str
    script: str
    port: Optional[int]
    auto_start: bool = False
    restart_on_crash: bool = True
    max_restarts: int = 5
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    working_dir: Optional[str] = None

    @property
    def script_path(self) -> Path:
        return BASE_DIR / self.script


def load_services() -> Dict[str, ServiceConfig]:
    """Load all services from services.yaml into typed dataclasses."""
    raw = _registry.list_services()
    services = {}
    for key, cfg in raw.items():
        services[key] = ServiceConfig(
            name=cfg.get("name", key),
            script=cfg.get("script", ""),
            port=cfg.get("port"),
            auto_start=cfg.get("auto_start", False),
            restart_on_crash=cfg.get("restart_on_crash", True),
            max_restarts=cfg.get("max_restarts", 5),
            args=cfg.get("args", []),
            env=cfg.get("env", {}),
            working_dir=cfg.get("working_dir"),
        )
    return services
