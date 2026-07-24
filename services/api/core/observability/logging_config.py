import json
import logging
import time
from datetime import datetime, timezone
from core.security.secret_masker import redact_secrets


class StructuredJSONFormatter(logging.Formatter):
    """
    Formats log records into JSON structures with trace context and secret redaction.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        if hasattr(record, "trace_id"):
            log_obj["trace_id"] = record.trace_id
        if hasattr(record, "correlation_id"):
            log_obj["correlation_id"] = record.correlation_id

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Redact secrets before serializing
        redacted_obj = redact_secrets(log_obj)
        return json.dumps(redacted_obj)


def configure_structured_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredJSONFormatter())
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler]
