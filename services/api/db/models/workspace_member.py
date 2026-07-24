import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import relationship
from db.session import Base


class WorkspaceRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(SQLEnum(WorkspaceRole), nullable=False, default=WorkspaceRole.MEMBER)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", backref="workspace_memberships")

    __table_args__ = (
        Index("ix_workspace_member_unique", "workspace_id", "user_id", unique=True),
    )

    def __repr__(self):
        return f"<WorkspaceMember user={self.user_id} in {self.workspace_id} as {self.role.value}>"
