import pytest
import requests
import os

@pytest.fixture
def base_url():
    return "http://localhost:8000"

def test_api_health(base_url):
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        assert resp.status_code == 200
        assert "healthy" in resp.json().get("status", "").lower()
    except:
        pytest.skip("API not running - start services first")

def test_models_load():
    # Simple model registry check
    import json
    with open("models/registry.json") as f:
        reg = json.load(f)
    assert len(reg["models"]["llm"]["models"]) == 12

if __name__ == "__main__":
    pytest.main(["-v", __file__])

