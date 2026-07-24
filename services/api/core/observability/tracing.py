import logging
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TraceContext(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:16])

    def to_headers(self) -> Dict[str, str]:
        return {
            "X-Trace-ID": self.trace_id,
            "X-Correlation-ID": self.correlation_id,
            "X-Span-ID": self.span_id,
        }

    @classmethod
    def from_headers(cls, headers: Any) -> "TraceContext":
        trace_id = headers.get("X-Trace-ID") or str(uuid.uuid4())
        correlation_id = headers.get("X-Correlation-ID") or headers.get("X-Request-ID") or str(uuid.uuid4())
        span_id = str(uuid.uuid4())[:16]
        return cls(trace_id=trace_id, correlation_id=correlation_id, span_id=span_id)
