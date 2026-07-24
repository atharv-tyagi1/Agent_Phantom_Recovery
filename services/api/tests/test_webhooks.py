import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_webhook_push_event():
    headers = {
        "X-GitHub-Event": "push",
        "X-GitHub-Delivery": "delivery-uuid-001",
        "Content-Type": "application/json"
    }
    payload = {
        "ref": "refs/heads/main",
        "installation": {"id": 12345},
        "repository": {
            "id": 99999,
            "full_name": "agent-phantom/test-repo"
        },
        "head_commit": {
            "id": "abc123456789",
            "message": "fix: update validate.py logic",
            "added": [],
            "modified": ["services/api/core/engine/controller.py"],
            "removed": []
        }
    }
    response = client.post("/api/webhooks/github", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["processed", "ignored"]
