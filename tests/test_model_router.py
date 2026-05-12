"""Tests for multi-model router and anonymizer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))


class TestAnonymizer:
    def test_sanitize_nip(self):
        from src.core.anonymizer import Anonymizer
        anon = Anonymizer()
        text = "NIP pegawai: 198501012010011001 dan 196702121992031002"
        result = anon.sanitize(text)
        assert "198501012010011001" not in result.text
        assert result.risk_score > 0
        assert len(result.replacements) == 2

    def test_sanitize_email(self):
        from src.core.anonymizer import Anonymizer
        anon = Anonymizer()
        text = "Hubungi admin@bpkp.go.id atau support@example.com"
        result = anon.sanitize(text)
        assert "admin@bpkp.go.id" not in result.text
        assert "support@example.com" not in result.text

    def test_sanitize_entity(self):
        from src.core.anonymizer import Anonymizer
        anon = Anonymizer()
        text = "PDAM Palangka Raya melaporkan pendapatan naik"
        result = anon.sanitize(text, anonymize_entities=True)
        assert "PDAM Palangka Raya" not in result.text

    def test_restore(self):
        from src.core.anonymizer import Anonymizer
        anon = Anonymizer()
        text = "Email: test@example.com"
        result = anon.sanitize(text)
        restored = anon.restore(result.text)
        assert "test@example.com" in restored

    def test_quick_sanitize(self):
        from src.core.anonymizer import quick_sanitize
        result = quick_sanitize("NIK: 3175091234567890")
        assert "3175091234567890" not in result


class TestModelRouter:
    def test_provider_selection_low_complexity(self):
        from src.core.model_router import ModelRouter
        router = ModelRouter()
        provider = router._select_provider("Halo, apa kabar?", "low")
        assert provider == "local"

    def test_provider_selection_high_complexity(self):
        from src.core.model_router import ModelRouter
        router = ModelRouter()
        provider = router._select_provider("Generate finding draft with deep analysis", "high")
        # Will be "cloud" if API key is set, otherwise "local"
        assert provider in ("local", "cloud")

    def test_local_models_scanned(self):
        from src.core.model_router import LocalModelProvider
        provider = LocalModelProvider()
        assert isinstance(provider.available, list)

    def test_cloud_not_configured(self):
        import os
        original = os.environ.get("KUERA_CLOUD_API_KEY")
        os.environ["KUERA_CLOUD_API_KEY"] = ""
        from src.core.model_router import CloudModelProvider
        cloud = CloudModelProvider()
        assert cloud.enabled is False
        resp = cloud.generate("test")
        assert resp.error is not None
        if original is not None:
            os.environ["KUERA_CLOUD_API_KEY"] = original

    def test_build_audit_prompt_keuangan(self):
        from src.core.model_router import ModelRouter
        router = ModelRouter()
        prompt = router._build_audit_prompt({
            "total_bumd": 50, "roa_rendah": 5, "underperforming": 8, "anomaly_flags": 3
        }, "keuangan")
        assert "50" in prompt
        assert "ROA Rendah" in prompt

    def test_build_audit_prompt_spi(self):
        from src.core.model_router import ModelRouter
        router = ModelRouter()
        prompt = router._build_audit_prompt({
            "nilai_total": 3.5, "kategori": "CUKUP", "rekomendasi_count": 12
        }, "spi")
        assert "3.5" in prompt
        assert "CUKUP" in prompt
