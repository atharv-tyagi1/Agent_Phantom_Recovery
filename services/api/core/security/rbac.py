from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.user import User
from db.models.workspace_member import WorkspaceMember, WorkspaceRole
from db.models.workspace import Workspace
from db.models.project import Project


def verify_workspace_access(
    workspace_id: str,
    user_id: str,
    required_role: WorkspaceRole = WorkspaceRole.MEMBER,
    db: Session = None
) -> WorkspaceMember:
    """
    Enforces RBAC authorization rules and cross-tenant data isolation.
    """
    if not db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database session unavailable for RBAC validation"
        )

    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-tenant access forbidden: User is not a member of this workspace"
        )

    # Role Hierarchy: OWNER > ADMIN > MEMBER
    role_hierarchy = {
        WorkspaceRole.MEMBER: 1,
        WorkspaceRole.ADMIN: 2,
        WorkspaceRole.OWNER: 3,
    }

    user_level = role_hierarchy.get(member.role, 0)
    required_level = role_hierarchy.get(required_role, 1)

    if user_level < required_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions: Requires {required_role.value} role"
        )

    return member


def verify_project_tenant_access(
    project_id: str,
    user_id: str,
    db: Session
) -> Project:
    """
    Validates that the project belongs to a workspace where the user has membership.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.workspace_id:
        verify_workspace_access(project.workspace_id, user_id, required_role=WorkspaceRole.MEMBER, db=db)

    return project
