"""Tests for ProcessManager."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.core.service_registry import ServiceConfig
from src.core.process_manager import ProcessManager, ServiceStatus


def test_process_manager_init():
    services = {
        "test_svc": ServiceConfig(
            name="Test Service",
            script="test.py",
            port=9999,
            auto_start=False,
        )
    }
    pm = ProcessManager(services)
    assert "test_svc" in pm.statuses
    assert pm.statuses["test_svc"].state == "stopped"


def test_format_duration():
    assert ProcessManager._fmt_duration(45) == "45s"
    assert ProcessManager._fmt_duration(125) == "2m 5s"
    assert ProcessManager._fmt_duration(3665) == "1h 1m"


def test_service_status_dataclass():
    st = ServiceStatus(name="Foo", pid=1234, state="running")
    assert st.name == "Foo"
    assert st.pid == 1234
