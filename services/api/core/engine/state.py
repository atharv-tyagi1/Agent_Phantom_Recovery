import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExecutionStatus(str, enum.Enum):
    INITIALIZING = "INITIALIZING"
    PLANNING = "PLANNING"
    INVESTIGATING = "INVESTIGATING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    REVIEWING = "REVIEWING"
    RE_PLANNING = "RE_PLANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ExecutionSnapshot(BaseModel):
    execution_id: str
    task_id: str
    project_id: str
    status: ExecutionStatus = ExecutionStatus.INITIALIZING
    current_step: int = 0
    max_steps: int = 25
    working_memory: Dict[str, Any] = Field(default_factory=dict)
    modified_files: List[str] = Field(default_factory=list)
    checkpoint_hashes: List[str] = Field(default_factory=list)
    last_error: Optional[str] = None
    rejection_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
