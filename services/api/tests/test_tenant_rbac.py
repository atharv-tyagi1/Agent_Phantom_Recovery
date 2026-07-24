import pytest
import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session

import db.models
from db.session import SessionLocal, Base, engine
from db.models.user import User, UserRole
from db.models.workspace import Workspace
from db.models.workspace_member import WorkspaceMember, WorkspaceRole
from core.security.rbac import verify_workspace_access

Base.metadata.create_all(bind=engine)


@pytest.fixture
def rbac_setup():
    db: Session = SessionLocal()
    owner = User(id=str(uuid.uuid4()), email=f"owner_{str(uuid.uuid4())[:6]}@example.com", role=UserRole.USER)
    member = User(id=str(uuid.uuid4()), email=f"member_{str(uuid.uuid4())[:6]}@example.com", role=UserRole.USER)
    outsider = User(id=str(uuid.uuid4()), email=f"outsider_{str(uuid.uuid4())[:6]}@example.com", role=UserRole.USER)
    db.add_all([owner, member, outsider])
    db.commit()

    workspace = Workspace(id=str(uuid.uuid4()), name="RBAC Test WS", slug=f"ws-{str(uuid.uuid4())[:6]}", owner_id=owner.id)
    db.add(workspace)
    db.commit()

    m_owner = WorkspaceMember(workspace_id=workspace.id, user_id=owner.id, role=WorkspaceRole.OWNER)
    m_member = WorkspaceMember(workspace_id=workspace.id, user_id=member.id, role=WorkspaceRole.MEMBER)
    db.add_all([m_owner, m_member])
    db.commit()

    yield {"workspace": workspace, "owner": owner, "member": member, "outsider": outsider}

    db.delete(m_member)
    db.delete(m_owner)
    db.delete(workspace)
    db.delete(outsider)
    db.delete(member)
    db.delete(owner)
    db.commit()
    db.close()


def test_rbac_access_allowed(rbac_setup):
    db: Session = SessionLocal()
    try:
        ws = rbac_setup["workspace"]
        owner = rbac_setup["owner"]
        member = rbac_setup["member"]

        # Owner has member and admin rights
        m1 = verify_workspace_access(ws.id, owner.id, required_role=WorkspaceRole.MEMBER, db=db)
        assert m1.role == WorkspaceRole.OWNER

        # Member has member rights
        m2 = verify_workspace_access(ws.id, member.id, required_role=WorkspaceRole.MEMBER, db=db)
        assert m2.role == WorkspaceRole.MEMBER
    finally:
        db.close()


def test_rbac_insufficient_role(rbac_setup):
    db: Session = SessionLocal()
    try:
        ws = rbac_setup["workspace"]
        member = rbac_setup["member"]

        # Member trying to access ADMIN endpoint
        with pytest.raises(HTTPException) as exc_info:
            verify_workspace_access(ws.id, member.id, required_role=WorkspaceRole.ADMIN, db=db)
        assert exc_info.value.status_code == 403
    finally:
        db.close()


def test_cross_tenant_access_forbidden(rbac_setup):
    db: Session = SessionLocal()
    try:
        ws = rbac_setup["workspace"]
        outsider = rbac_setup["outsider"]

        # Outsider trying to access workspace
        with pytest.raises(HTTPException) as exc_info:
            verify_workspace_access(ws.id, outsider.id, required_role=WorkspaceRole.MEMBER, db=db)
        assert exc_info.value.status_code == 403
        assert "Cross-tenant access forbidden" in exc_info.value.detail
    finally:
        db.close()
