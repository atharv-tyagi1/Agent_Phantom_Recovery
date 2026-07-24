import re
from typing import Any, Dict, List, Union

REDACTED_TEXT = "***REDACTED***"

SENSITIVE_PATTERNS = [
    re.compile(r"(?i)api[_-]?key"),
    re.compile(r"(?i)secret"),
    re.compile(r"(?i)token"),
    re.compile(r"(?i)password"),
    re.compile(r"(?i)authorization"),
    re.compile(r"(?i)jwt"),
    re.compile(r"(?i)private[_-]?key"),
    re.compile(r"(?i)access[_-]?token"),
]


def is_sensitive_key(key: str) -> bool:
    if not isinstance(key, str):
        return False
    return any(pattern.search(key) for pattern in SENSITIVE_PATTERNS)


def redact_secrets(data: Any) -> Any:
    """
    Recursively redacts sensitive dictionary keys, list values, or text snippets.
    """
    if isinstance(data, dict):
        cleaned: Dict[str, Any] = {}
        for k, v in data.items():
            if is_sensitive_key(k):
                cleaned[k] = REDACTED_TEXT
            else:
                cleaned[k] = redact_secrets(v)
        return cleaned
    elif isinstance(data, list):
        return [redact_secrets(item) for item in data]
    elif isinstance(data, str):
        # Mask inline bearer tokens if present in string text
        if "Bearer " in data or "ghp_" in data or "nvapi-" in data:
            return re.sub(r"(Bearer\s+)[A-Za-z0-9\._\-]+", r"\1***REDACTED***", data)
        return data
    return data
