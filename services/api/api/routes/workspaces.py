from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid

from db.session import get_db
from db.models.workspace import Workspace
from db.models.workspace_member import WorkspaceMember, WorkspaceRole
from db.models.user import User
from core.auth import get_current_user

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    slug: str
    owner_id: str
    created_at: str

    class Config:
        from_attributes = True


class WorkspaceMemberResponse(BaseModel):
    id: str
    user_id: str
    role: str
    joined_at: str

    class Config:
        from_attributes = True


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    slug = f"{payload.name.lower().replace(' ', '-')}-{str(uuid.uuid4())[:6]}"
    workspace = Workspace(
        name=payload.name,
        slug=slug,
        owner_id=current_user.id
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role=WorkspaceRole.OWNER
    )
    db.add(member)
    db.commit()

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        owner_id=workspace.owner_id,
        created_at=workspace.created_at.isoformat() if workspace.created_at else ""
    )


@router.get("", response_model=List[WorkspaceResponse])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    memberships = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).all()
    workspace_ids = [m.workspace_id for m in memberships]
    workspaces = db.query(Workspace).filter(Workspace.id.in_(workspace_ids)).all()
    return [
        WorkspaceResponse(
            id=w.id,
            name=w.name,
            slug=w.slug,
            owner_id=w.owner_id,
            created_at=w.created_at.isoformat() if w.created_at else ""
        )
        for w in workspaces
    ]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Workspace not found or access denied")

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        owner_id=workspace.owner_id,
        created_at=workspace.created_at.isoformat() if workspace.created_at else ""
    )
