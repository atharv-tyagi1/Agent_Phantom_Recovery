import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Dict, Any, Tuple
from core.config import settings


def generate_pkce_pair() -> Tuple[str, str]:
    """
    Generates a cryptographically random code_verifier and its SHA-256 code_challenge.
    """
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    return verifier, challenge


def create_oauth_state(workspace_id: str = "", extra_data: Dict[str, Any] = None) -> str:
    """
    Creates an HMAC-signed OAuth state string encoding timestamp, workspace_id, and nonce.
    """
    now = int(time.time())
    payload = {
        "timestamp": now,
        "workspace_id": workspace_id,
        "nonce": secrets.token_hex(16),
        "data": extra_data or {},
    }
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    signature = hmac.new(
        settings.SUPABASE_JWT_SECRET.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return f"{encoded_payload}.{signature}"


def validate_oauth_state(state_token: str, max_age_seconds: int = 600) -> Dict[str, Any]:
    """
    Validates HMAC signature, age, and integrity of the OAuth state token.
    Raises ValueError on invalid signature or expiration.
    """
    if not state_token or "." not in state_token:
        raise ValueError("Malformed state token format")

    encoded_payload, signature = state_token.rsplit(".", 1)

    expected_sig = hmac.new(
        settings.SUPABASE_JWT_SECRET.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, signature):
        raise ValueError("Invalid OAuth state signature")

    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_payload.encode("utf-8"))
        payload = json.loads(decoded_bytes.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"Failed to parse state payload: {e}")

    now = int(time.time())
    ts = payload.get("timestamp", 0)
    if now - ts > max_age_seconds:
        raise ValueError("OAuth state token has expired")

    return payload
