import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, BigInteger, JSON, Enum as SQLEnum, ForeignKey, Text
from db.session import Base


class WebhookStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    IGNORED = "ignored"


class WebhookEvent(Base):
    """
    Audit log of all incoming GitHub Webhook events.
    Enforces idempotency using X-GitHub-Delivery header as unique delivery_id.
    """
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    delivery_id = Column(String(255), unique=True, nullable=False, index=True)
    github_event_type = Column(String(100), nullable=False, index=True)
    installation_id = Column(BigInteger, nullable=True, index=True)
    repository_id = Column(String, ForeignKey("repositories.id", ondelete="SET NULL"), nullable=True, index=True)
    payload = Column(JSON, nullable=False)
    status = Column(SQLEnum(WebhookStatus), nullable=False, default=WebhookStatus.PENDING)
    error_message = Column(Text, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<WebhookEvent {self.github_event_type} ({self.delivery_id}) - {self.status.value}>"
