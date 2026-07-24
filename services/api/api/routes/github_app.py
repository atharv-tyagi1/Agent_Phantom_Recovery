from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from core.config import settings
from core.auth import get_current_user
from core.github.client import GitHubClient
from db.session import get_db
from db.models.github_app_installation import GitHubAppInstallation
from db.models.workspace import Workspace
from db.models.repository import Repository
from db.models.project import Project
from db.models.user import User

router = APIRouter(prefix="/github/app", tags=["GitHub App"])


class ConnectRepoRequest(BaseModel):
    project_id: str
    github_repo_id: int
    name: str
    full_name: str
    git_url: str
    default_branch: str = "main"


@router.get("/install")
def get_app_install_url(workspace_id: str):
    """Returns redirect URL for installing the Agent Phantom GitHub App."""
    install_url = f"https://github.com/apps/agent-phantom-recovery/installations/new?state={workspace_id}"
    return {"url": install_url}


@router.get("/callback")
def github_app_callback(
    installation_id: int = Query(...),
    state: str = Query(...),  # workspace_id
    db: Session = Depends(get_db)
):
    """Callback after GitHub App installation."""
    workspace = db.query(Workspace).filter(Workspace.id == state).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    existing = db.query(GitHubAppInstallation).filter(
        GitHubAppInstallation.installation_id == installation_id
    ).first()

    if not existing:
        installation = GitHubAppInstallation(
            workspace_id=workspace.id,
            installation_id=installation_id,
            account_login="github-account",
            account_type="Organization",
            repository_selection="all",
        )
        db.add(installation)
        db.commit()
        db.refresh(installation)
        existing = installation

    return {
        "status": "success",
        "installation_id": existing.installation_id,
        "workspace_id": existing.workspace_id
    }


@router.get("/installations/{installation_id}/repos")
async def list_installation_repos(
    installation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch repositories accessible via GitHub App installation token."""
    inst = db.query(GitHubAppInstallation).filter(
        GitHubAppInstallation.installation_id == installation_id
    ).first()
    if not inst:
        raise HTTPException(status_code=404, detail="GitHub App installation not found")

    token = await GitHubClient.get_installation_access_token(installation_id)
    repos = await GitHubClient.list_installation_repositories(token)
    return repos


@router.post("/installations/{installation_id}/connect-repo")
async def connect_installation_repo(
    installation_id: int,
    payload: ConnectRepoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Connect a GitHub repository to a project using App installation token."""
    inst = db.query(GitHubAppInstallation).filter(
        GitHubAppInstallation.installation_id == installation_id
    ).first()
    if not inst:
        raise HTTPException(status_code=404, detail="GitHub App installation not found")

    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    repo = Repository(
        project_id=payload.project_id,
        installation_id=inst.id,
        github_repo_id=payload.github_repo_id,
        name=payload.name,
        full_name=payload.full_name,
        git_url=payload.git_url,
        default_branch=payload.default_branch,
        clone_status="pending"
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)

    # Initialize default monitoring settings
    from db.models.repository_monitoring import RepositoryMonitoringSettings, MonitoringMode
    monitoring = RepositoryMonitoringSettings(
        repository_id=repo.id,
        mode=MonitoringMode.AUTO_INVESTIGATE,
        trigger_on_push=True,
        trigger_on_pr=True
    )
    db.add(monitoring)
    db.commit()

    return {
        "status": "connected",
        "repository_id": repo.id,
        "full_name": repo.full_name,
        "clone_status": repo.clone_status
    }
