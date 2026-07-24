import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_github_login_url():
    response = client.get("/auth/github/login")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "github.com/login/oauth/authorize" in data["url"]


def test_github_oauth_callback_mock():
    response = client.post("/auth/github/callback", json={"code": "mock_code_123"})
    if response.status_code != 200:
        print("CALLBACK ERROR RESPONSE:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "octocat@github.com"
