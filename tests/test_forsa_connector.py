"""Tests for FORSA BUMDes WSL bridge."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.data.forsa_connector import ForsaBridge


class TestForsaBridge:
    def test_wsl_check(self):
        bridge = ForsaBridge()
        status = bridge.check_wsl_status()
        assert "wsl_available" in status
        assert "forsa_scripts_found" in status
        # Either WSL exists or not — both are valid states
        assert isinstance(status["wsl_available"], bool)

    def test_parse_output(self):
        bridge = ForsaBridge()
        lines = [
            "Total BUMD: 50",
            "Sudah isi: 30",
            "Belum isi: 20",
            "BUMD A | Sudah | Lengkap",
            "BUMD B | Belum | -",
        ]
        parsed = bridge._parse_check_status_output(lines)
        assert parsed["total_bumd"] == 50
        assert parsed["sudah_isi"] == 30
        assert parsed["belum_isi"] == 20
        assert len(parsed["status_list"]) == 2

    def test_parse_empty(self):
        bridge = ForsaBridge()
        parsed = bridge._parse_check_status_output([])
        assert parsed["total_bumd"] == 0
        assert parsed["status_list"] == []

    def test_parse_malformed(self):
        bridge = ForsaBridge()
        lines = [
            "Some random line",
            "Total BUMD: abc",
            "BUMD C | Invalid",
        ]
        parsed = bridge._parse_check_status_output(lines)
        assert parsed["total_bumd"] == 0
        # Malformed line may still be parsed loosely
        assert isinstance(parsed["status_list"], list)

    def test_bridge_init(self):
        bridge = ForsaBridge()
        assert hasattr(bridge, 'wsl_available')
        assert hasattr(bridge, 'WSL_SCRIPT_DIR')
        assert hasattr(bridge, 'DEFAULT_SCRIPT')


class TestForsaAPI:
    def test_forsa_status_endpoint(self):
        from fastapi.testclient import TestClient
        from src.web.api import app
        client = TestClient(app)
        r = client.get("/api/audit/forsa/status")
        assert r.status_code == 200
        assert "wsl_available" in r.json()

    def test_forsa_files_endpoint(self):
        from fastapi.testclient import TestClient
        from src.web.api import app
        client = TestClient(app)
        r = client.get("/api/audit/forsa/files")
        assert r.status_code == 200
        assert "files" in r.json()

    def test_forsa_run_endpoint(self):
        from fastapi.testclient import TestClient
        from src.web.api import app
        client = TestClient(app)
        r = client.post("/api/audit/forsa/run", json={"mode": "2"})
        assert r.status_code == 200
        data = r.json()
        assert "status" in data
