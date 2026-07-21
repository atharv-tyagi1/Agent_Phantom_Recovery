from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from db.models.repository import Repository
from db.models.project import Project
from db.models.user import User
from api.schemas.repository import RepositoryCreate, RepositoryUpdate, RepositoryResponse
from core.auth import get_current_user

router = APIRouter(prefix="/projects/{project_id}/repositories", tags=["Repositories"])

def get_project_or_404(db: Session, project_id: str, user_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
def create_repository(
    project_id: str,
    repo_in: RepositoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_project_or_404(db, project_id, current_user.id)
    
    repository = Repository(
        project_id=project_id,
        **repo_in.model_dump()
    )
    db.add(repository)
    db.commit()
    db.refresh(repository)
    return repository

@router.get("", response_model=List[RepositoryResponse])
def list_repositories(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    get_project_or_404(db, project_id, current_user.id)
    
    repos = db.query(Repository).filter(
        Repository.project_id == project_id
    ).offset(skip).limit(limit).all()
    return repos

@router.get("/{repo_id}", response_model=RepositoryResponse)
def get_repository(
    project_id: str,
    repo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_project_or_404(db, project_id, current_user.id)
    
    repo = db.query(Repository).filter(
        Repository.id == repo_id,
        Repository.project_id == project_id
    ).first()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo

@router.delete("/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repository(
    project_id: str,
    repo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_project_or_404(db, project_id, current_user.id)
    
    repo = db.query(Repository).filter(
        Repository.id == repo_id,
        Repository.project_id == project_id
    ).first()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    db.delete(repo)
    db.commit()
    return None
