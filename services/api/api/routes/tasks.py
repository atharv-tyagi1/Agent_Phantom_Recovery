from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from db.session import get_db
from db.models.task import Task, TaskStatus
from db.models.project import Project
from db.models.user import User
from api.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from core.auth import get_current_user
from core.events import TaskCreatedEvent, emit_event

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["Tasks"])

def get_project_or_404(db: Session, project_id: str, user_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: str,
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_project_or_404(db, project_id, current_user.id)
    
    task = Task(
        project_id=project_id,
        **task_in.model_dump()
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Emit Audit Event
    event = TaskCreatedEvent(
        payload={"task_id": task.id, "title": task.title}
    )
    emit_event(event, db, user_id=current_user.id, project_id=project_id)

    return task

@router.get("", response_model=List[TaskResponse])
def list_tasks(
    project_id: str,
    status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    get_project_or_404(db, project_id, current_user.id)
    
    query = db.query(Task).filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
        
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    project_id: str,
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_project_or_404(db, project_id, current_user.id)
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    project_id: str,
    task_id: str,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_project_or_404(db, project_id, current_user.id)
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
        
    db.commit()
    db.refresh(task)
    return task
