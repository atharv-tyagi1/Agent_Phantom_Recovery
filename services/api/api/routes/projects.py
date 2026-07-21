from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from db.models.project import Project, ProjectStatus
from db.models.user import User
from api.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from core.auth import get_current_user
from core.events import ProjectCreatedEvent, emit_event

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = Project(
        owner_id=current_user.id,
        **project_in.model_dump()
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Emit Audit Event
    event = ProjectCreatedEvent(
        payload={"project_id": project.id, "name": project.name}
    )
    emit_event(event, db, user_id=current_user.id, project_id=project.id)

    return project

@router.get("", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    projects = db.query(Project).filter(
        Project.owner_id == current_user.id,
        Project.status != ProjectStatus.ARCHIVED
    ).offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
        
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project.status = ProjectStatus.ARCHIVED
    db.commit()
    return None
