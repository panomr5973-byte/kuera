"""Tests for configuration loading."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.utils.config import Settings, ServiceRegistry, settings, registry


def test_settings_loaded():
    assert settings.app_name == "KUERA Unified Desktop"
    assert settings.control_panel_port == 7777
    assert settings.base_dir.exists()


def test_service_registry_loaded():
    services = registry.list_services()
    assert "kuera_api" in services
    assert services["kuera_api"]["port"] == 8000


def test_load_services_dataclass():
    from src.core.service_registry import load_services
    services = load_services()
    assert "kuera_api" in services
    assert services["kuera_api"].name == "Kuera Production API"
    assert services["kuera_api"].port == 8000
