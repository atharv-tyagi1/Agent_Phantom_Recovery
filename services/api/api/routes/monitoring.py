from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from db.session import get_db
from db.models.repository import Repository
from db.models.repository_monitoring import RepositoryMonitoringSettings, MonitoringMode
from db.models.user import User
from core.auth import get_current_user

router = APIRouter(prefix="/repositories/{repository_id}/monitoring", tags=["Repository Monitoring"])


class MonitoringSettingsUpdate(BaseModel):
    mode: Optional[MonitoringMode] = None
    trigger_on_push: Optional[bool] = None
    trigger_on_pr: Optional[bool] = None
    trigger_on_merge: Optional[bool] = None
    branch_filter: Optional[List[str]] = None
    max_executions_per_day: Optional[int] = None


class MonitoringSettingsResponse(BaseModel):
    id: str
    repository_id: str
    mode: str
    trigger_on_push: bool
    trigger_on_pr: bool
    trigger_on_merge: bool
    branch_filter: List[str]
    max_executions_per_day: int

    class Config:
        from_attributes = True


@router.get("", response_model=MonitoringSettingsResponse)
def get_monitoring_settings(
    repository_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    settings_obj = db.query(RepositoryMonitoringSettings).filter(
        RepositoryMonitoringSettings.repository_id == repository_id
    ).first()

    if not settings_obj:
        settings_obj = RepositoryMonitoringSettings(repository_id=repository_id)
        db.add(settings_obj)
        db.commit()
        db.refresh(settings_obj)

    return settings_obj


@router.put("", response_model=MonitoringSettingsResponse)
def update_monitoring_settings(
    repository_id: str,
    payload: MonitoringSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    settings_obj = db.query(RepositoryMonitoringSettings).filter(
        RepositoryMonitoringSettings.repository_id == repository_id
    ).first()

    if not settings_obj:
        settings_obj = RepositoryMonitoringSettings(repository_id=repository_id)
        db.add(settings_obj)

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(settings_obj, field, val)

    db.commit()
    db.refresh(settings_obj)
    return settings_obj
