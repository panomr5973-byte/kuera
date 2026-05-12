"""Tests for canonical KUERA API (src/web/api.py)."""

import pytest
from fastapi.testclient import TestClient

# Need to set path before import
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.web.api import app

client = TestClient(app)


class TestAPIHealth:
    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["app"] == "KUERA AI API"
        assert "version" in r.json()

    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert "timestamp" in data

    def test_models_list(self):
        r = client.get("/models")
        assert r.status_code == 200
        assert "models" in r.json()

    def test_model_not_found(self):
        r = client.get("/models/nonexistent_model_xyz")
        assert r.status_code == 404


class TestAPIAudit:
    def test_audit_templates(self):
        r = client.get("/api/audit/templates")
        assert r.status_code == 200
        data = r.json()
        assert "templates" in data
        assert len(data["templates"]) == 3

    def test_audit_run_missing_params(self):
        r = client.post("/api/audit/run", json={})
        assert r.status_code == 400

    def test_audit_run_invalid_jenis(self):
        r = client.post("/api/audit/run", json={"jenis": "invalid", "filename": "test.xlsx"})
        assert r.status_code == 400

    def test_audit_chart_missing_params(self):
        r = client.post("/api/audit/chart", json={})
        assert r.status_code == 400


class TestAPIAuditTrail:
    def test_audit_history_empty(self):
        r = client.get("/api/audit/history")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "runs" in data

    def test_audit_history_with_jenis_filter(self):
        r = client.get("/api/audit/history?jenis=keuangan&limit=5")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"

    def test_audit_history_detail_not_found(self):
        r = client.get("/api/audit/history/999999")
        assert r.status_code == 404


class TestAPIAuditUpload:
    def test_audit_upload_no_file(self):
        r = client.post("/api/audit/upload")
        assert r.status_code == 422  # FastAPI requires file

    def test_audit_upload_invalid_extension(self):
        r = client.post(
            "/api/audit/upload",
            files={"file": ("test.txt", b"not an excel", "text/plain")},
        )
        assert r.status_code == 400


class TestAPIAuditExport:
    def test_audit_export_pdf_missing_params(self):
        r = client.post("/api/audit/export/pdf", json={})
        assert r.status_code == 400

    def test_audit_export_pdf_unsupported_jenis(self):
        r = client.post("/api/audit/export/pdf", json={"jenis": "spi", "summary": {"a": 1}})
        assert r.status_code == 501


class TestAPIBatch:
    def test_batch_predict_no_model(self):
        r = client.post("/predict/batch", json={"model_id": "nonexistent", "inputs": [{"a": 1}]})
        assert r.status_code == 404

    def test_batch_predict_no_input(self):
        r = client.post("/predict/batch", json={"model_id": "best_model_logistic_regression", "inputs": []})
        assert r.status_code == 400


class TestAPIFeedback:
    def test_feedback(self):
        r = client.post("/feedback", json={"interaction_id": 1, "feedback": 1, "reason": "Good"})
        assert r.status_code == 200
        assert r.json()["status"] == "success"
