import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_healthz_liveness_probe():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_livez_liveness_probe():
    response = client.get("/livez")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readyz_readiness_probe():
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_trace_header_propagation():
    response = client.get("/healthz", headers={"X-Request-ID": "req-uuid-12345"})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "req-uuid-12345"
    assert "X-Trace-ID" in response.headers
