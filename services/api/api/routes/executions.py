from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from db.models.execution import Execution
from db.models.task import Task
from db.models.project import Project
from db.models.user import User
from api.schemas.execution import ExecutionCreate, ExecutionResponse
from core.auth import get_current_user
from core.events import ExecutionStartedEvent, emit_event

router = APIRouter(prefix="/tasks/{task_id}/executions", tags=["Executions"])

def get_task_and_verify_access(db: Session, task_id: str, user_id: str) -> Task:
    # Find the task and join with project to verify owner
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == user_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or access denied")
    return task

@router.post("", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
def create_execution(
    task_id: str,
    execution_in: ExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = get_task_and_verify_access(db, task_id, current_user.id)
    
    execution = Execution(
        task_id=task_id,
        project_id=task.project_id,
        **execution_in.model_dump()
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    # Emit Audit Event
    event = ExecutionStartedEvent(
        payload={"execution_id": execution.id, "task_id": task_id}
    )
    emit_event(event, db, user_id=current_user.id, project_id=task.project_id)

    return execution

@router.get("", response_model=List[ExecutionResponse])
def list_executions(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    get_task_and_verify_access(db, task_id, current_user.id)
    
    executions = db.query(Execution).filter(
        Execution.task_id == task_id
    ).offset(skip).limit(limit).all()
    return executions

@router.get("/{exec_id}", response_model=ExecutionResponse)
def get_execution(
    task_id: str,
    exec_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_task_and_verify_access(db, task_id, current_user.id)
    
    execution = db.query(Execution).filter(
        Execution.id == exec_id,
        Execution.task_id == task_id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution
