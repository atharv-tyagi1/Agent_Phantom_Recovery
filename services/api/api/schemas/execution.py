from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from db.models.execution import ExecutionStatus

class ExecutionBase(BaseModel):
    goal: str

class ExecutionCreate(ExecutionBase):
    pass

class ExecutionResponse(ExecutionBase):
    id: str
    task_id: str
    project_id: str
    status: ExecutionStatus
    current_phase: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
