import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from db.models.audit_log import AuditLog

class BaseEvent(BaseModel):
    event_name: str
    event_version: str = "v1.0"
    schema_version: str = "1.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payload: Dict[str, Any]

class ProjectCreatedEvent(BaseEvent):
    event_name: str = "ProjectCreated"

class TaskCreatedEvent(BaseEvent):
    event_name: str = "TaskCreated"

class ExecutionStartedEvent(BaseEvent):
    event_name: str = "ExecutionStarted"

class TaskFailedEvent(BaseEvent):
    event_name: str = "TaskFailed"
    execution_id: str
    task_id: str
    failure_reason: str

def emit_event(
    event: BaseEvent,
    db: Session,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None
) -> AuditLog:
    """
    Writes an event to the audit_logs table.
    """
    audit_log = AuditLog(
        event_type=event.event_name,
        event_version=event.event_version,
        correlation_id=event.correlation_id,
        user_id=user_id,
        project_id=project_id,
        payload=event.model_dump(mode="json"),
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log
