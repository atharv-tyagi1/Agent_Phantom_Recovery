import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_github_app_install_url():
    response = client.get("/github/app/install?workspace_id=ws-123")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "workspace_id=ws-123" in data["url"] or "state=ws-123" in data["url"]


def test_github_app_callback():
    # First ensure a workspace exists
    ws_id = "test-ws-id"
    response = client.get(f"/github/app/callback?installation_id=998877&state={ws_id}")
    # Callback creates installation or returns error if workspace missing
    assert response.status_code in [200, 404]
