from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Dict, Any

class BaseEvent(BaseModel):
    event_name: str
    event_version: str = "v1.0"
    schema_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payload: Dict[str, Any]

class TaskCreatedEvent(BaseEvent):
    event_name: str = "TaskCreated"

class ToolCompletedEvent(BaseEvent):
    event_name: str = "ToolCompleted"

class VerificationPassedEvent(BaseEvent):
    event_name: str = "VerificationPassed"

class TaskFailedEvent(BaseEvent):
    event_name: str = "TaskFailed"
    execution_id: str
    task_id: str
    failure_reason: str
