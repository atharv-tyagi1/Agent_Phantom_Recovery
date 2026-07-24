import pytest
from fastapi.testclient import TestClient
from main import app
from core.security.secret_masker import redact_secrets
from core.security.sanitizers import sanitize_file_path, sanitize_command
from core.security.oauth_pkce import generate_pkce_pair, create_oauth_state, validate_oauth_state

client = TestClient(app)


def test_security_headers():
    response = client.get("/healthz")
    assert response.status_code == 200
    headers = response.headers
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Content-Security-Policy" in headers


def test_secret_masker():
    payload = {
        "user_email": "test@example.com",
        "api_key": "nvapi-secret12345",
        "access_token": "ghp_secretToken999",
        "nested": {"client_secret": "super_secret"},
    }
    redacted = redact_secrets(payload)
    assert redacted["api_key"] == "***REDACTED***"
    assert redacted["access_token"] == "***REDACTED***"
    assert redacted["nested"]["client_secret"] == "***REDACTED***"
    assert redacted["user_email"] == "test@example.com"


def test_sanitizers():
    # Test valid path
    valid = sanitize_file_path("project/main.py", base_dir="workspaces")
    assert "workspaces" in valid

    # Test path traversal attack prevention
    with pytest.raises(Exception):
        sanitize_file_path("../../etc/passwd", base_dir="workspaces")

    # Test command injection prevention
    with pytest.raises(Exception):
        sanitize_command("ls -la; rm -rf /")


def test_oauth_pkce_and_state():
    verifier, challenge = generate_pkce_pair()
    assert len(verifier) > 50
    assert len(challenge) > 20

    state = create_oauth_state(workspace_id="ws-999")
    parsed = validate_oauth_state(state)
    assert parsed["workspace_id"] == "ws-999"

    # Test invalid signature
    with pytest.raises(ValueError):
        validate_oauth_state(state + "invalid")
