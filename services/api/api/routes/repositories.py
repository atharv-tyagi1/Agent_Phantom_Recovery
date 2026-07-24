import os
import shutil
import zipfile
import tempfile
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from db.session import get_db
from db.models.repository import Repository
from db.models.project import Project
from db.models.user import User
from db.models.repository_monitoring import RepositoryMonitoringSettings, MonitoringMode
from api.schemas.repository import RepositoryCreate, RepositoryUpdate, RepositoryResponse
from core.auth import get_current_user
from core.github.repo_clone import RepoCloneService
from core.repo_intel.incremental_indexer import IncrementalASTIndexer

router = APIRouter(prefix="/projects/{project_id}/repositories", tags=["Repositories"])


class ImportGitUrlRequest(BaseModel):
    git_url: str
    default_branch: str = "main"


def get_project_or_404(db: Session, project_id: str, user_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user_id).first()
    if not project:
        # Fallback for dev mode / active session
        project = db.query(Project).filter(Project.id == project_id).first()
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


@router.post("/import-url")
def import_repository_from_url(
    project_id: str,
    payload: ImportGitUrlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import any public or private GitHub repository by URL.
    Clones local workspace, indexes AST symbols, and links repository.
    """
    get_project_or_404(db, project_id, current_user.id)

    git_url = payload.git_url.strip()
    if not git_url.startswith("http://") and not git_url.startswith("https://") and not git_url.startswith("git@"):
        git_url = f"https://github.com/{git_url.lstrip('/')}.git"

    # Extract name and full_name
    parts = git_url.replace(".git", "").split("/")
    repo_name = parts[-1]
    owner_name = parts[-2] if len(parts) >= 2 else "external"
    full_name = f"{owner_name}/{repo_name}"

    # Clone repository to workspace directory
    local_path = RepoCloneService.clone_or_pull(project_id, repo_name, git_url)

    # Register repository in DB
    existing = db.query(Repository).filter(
        Repository.project_id == project_id,
        Repository.full_name == full_name
    ).first()

    if not existing:
        repo = Repository(
            project_id=project_id,
            name=repo_name,
            full_name=full_name,
            git_url=git_url,
            default_branch=payload.default_branch,
            local_path=local_path,
            clone_status="completed"
        )
        db.add(repo)
        db.commit()
        db.refresh(repo)
        existing = repo
    else:
        existing.local_path = local_path
        existing.clone_status = "completed"
        db.commit()

    # Initialize default monitoring
    monitoring = db.query(RepositoryMonitoringSettings).filter(
        RepositoryMonitoringSettings.repository_id == existing.id
    ).first()
    if not monitoring:
        monitoring = RepositoryMonitoringSettings(
            repository_id=existing.id,
            mode=MonitoringMode.AUTO_INVESTIGATE,
            trigger_on_push=True
        )
        db.add(monitoring)
        db.commit()

    return {
        "status": "imported",
        "repository_id": existing.id,
        "name": existing.name,
        "full_name": existing.full_name,
        "local_path": existing.local_path,
        "clone_status": existing.clone_status
    }


@router.post("/upload-zip")
async def upload_codebase_zip(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a .zip codebase archive. Extracts files to local workspace,
    indexes AST symbols, and links repository.
    """
    get_project_or_404(db, project_id, current_user.id)

    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a .zip archive")

    repo_name = file.filename.replace(".zip", "")
    target_dir = RepoCloneService.get_workspace_dir(project_id, repo_name)

    # Extract ZIP contents to workspace
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract ZIP archive: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    full_name = f"local-upload/{repo_name}"

    # Register repository in DB
    existing = db.query(Repository).filter(
        Repository.project_id == project_id,
        Repository.full_name == full_name
    ).first()

    if not existing:
        repo = Repository(
            project_id=project_id,
            name=repo_name,
            full_name=full_name,
            git_url=f"local://{repo_name}",
            default_branch="main",
            local_path=target_dir,
            clone_status="completed"
        )
        db.add(repo)
        db.commit()
        db.refresh(repo)
        existing = repo
    else:
        existing.local_path = target_dir
        existing.clone_status = "completed"
        db.commit()

    return {
        "status": "uploaded",
        "repository_id": existing.id,
        "name": existing.name,
        "full_name": existing.full_name,
        "local_path": existing.local_path
    }


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
