import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import relationship
from db.session import Base
from db.models.workspace_member import WorkspaceRole


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"


class WorkspaceInvitation(Base):
    """
    Expiring, single-use invitation tokens for joining a Workspace.
    """
    __tablename__ = "workspace_invitations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    role = Column(SQLEnum(WorkspaceRole), nullable=False, default=WorkspaceRole.MEMBER)
    token = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(InvitationStatus), nullable=False, default=InvitationStatus.PENDING)
    invited_by_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace = relationship("Workspace", backref="invitations")
    invited_by = relationship("User", backref="sent_workspace_invitations")

    def __repr__(self):
        return f"<WorkspaceInvitation {self.email} in {self.workspace_id} ({self.status.value})>"
