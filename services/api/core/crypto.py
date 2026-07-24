import base64
import os
from cryptography.fernet import Fernet
from core.config import settings

def _get_fernet_key() -> bytes:
    key_str = settings.FERNET_ENCRYPTION_KEY
    try:
        key_bytes = key_str.encode("utf-8")
        # Validate if key is a valid Fernet key
        Fernet(key_bytes)
        return key_bytes
    except Exception:
        # Fallback to deterministic key derivation if invalid format
        key_32 = key_str.ljust(32)[:32].encode("utf-8")
        return base64.urlsafe_b64encode(key_32)

def encrypt_token(plain_token: str) -> str:
    """Encrypt plain text token using Fernet AES-256."""
    if not plain_token:
        return ""
    fernet = Fernet(_get_fernet_key())
    return fernet.encrypt(plain_token.encode("utf-8")).decode("utf-8")

def decrypt_token(encrypted_token: str) -> str:
    """Decrypt Fernet-encrypted token."""
    if not encrypted_token:
        return ""
    try:
        fernet = Fernet(_get_fernet_key())
        return fernet.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")
    except Exception:
        return encrypted_token
