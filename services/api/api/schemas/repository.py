from pydantic import BaseModel, ConfigDict, AnyHttpUrl
from typing import Optional
from datetime import datetime

class RepositoryBase(BaseModel):
    name: str
    git_url: str
    default_branch: str = "main"

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryUpdate(BaseModel):
    name: Optional[str] = None
    default_branch: Optional[str] = None
    local_path: Optional[str] = None
    last_indexed_at: Optional[datetime] = None

class RepositoryResponse(RepositoryBase):
    id: str
    project_id: str
    local_path: Optional[str] = None
    last_indexed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
