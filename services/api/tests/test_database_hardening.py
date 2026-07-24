import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

import db.models
from db.session import get_db, SessionLocal, Base, engine
from db.models.user import User, UserRole
from db.models.workspace import Workspace
from db.models.workspace_invitation import WorkspaceInvitation, InvitationStatus
from db.models.workspace_audit_log import WorkspaceAuditLog
from db.models.workspace_member import WorkspaceRole

# Ensure all database tables exist in the test DB
Base.metadata.create_all(bind=engine)


@pytest.fixture
def sample_workspace():
    db: Session = SessionLocal()
    user = User(
        id=str(uuid.uuid4()),
        supabase_id=f"sub_{str(uuid.uuid4())[:8]}",
        email=f"owner_{str(uuid.uuid4())[:6]}@example.com",
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()

    workspace = Workspace(
        id=str(uuid.uuid4()),
        name="Test Workspace",
        slug=f"ws-{str(uuid.uuid4())[:6]}",
        owner_id=user.id,
    )
    db.add(workspace)
    db.commit()

    yield workspace

    db.delete(workspace)
    db.delete(user)
    db.commit()
    db.close()


def test_workspace_invitation_model(sample_workspace):
    db: Session = SessionLocal()
    try:
        invitation = WorkspaceInvitation(
            workspace_id=sample_workspace.id,
            email="invited@example.com",
            role=WorkspaceRole.MEMBER,
            token=f"invite-token-{uuid.uuid4()}",
            status=InvitationStatus.PENDING,
            expires_at=datetime.now(timezone.utc)
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)

        assert invitation.id is not None
        assert invitation.status == InvitationStatus.PENDING

        # Cleanup
        db.delete(invitation)
        db.commit()
    finally:
        db.close()


def test_workspace_audit_log_model(sample_workspace):
    db: Session = SessionLocal()
    try:
        log = WorkspaceAuditLog(
            workspace_id=sample_workspace.id,
            action="MEMBER_ADDED",
            target_resource="user@example.com",
            payload={"role": "admin"}
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        assert log.id is not None
        assert log.action == "MEMBER_ADDED"

        # Cleanup
        db.delete(log)
        db.commit()
    finally:
        db.close()
