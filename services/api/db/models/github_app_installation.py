import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, BigInteger, JSON, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base


class GitHubAppInstallation(Base):
    """
    Maps a GitHub App Installation to a Workspace.
    Automation Layer uses installation tokens (NOT OAuth access tokens).
    """
    __tablename__ = "github_app_installations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    installation_id = Column(BigInteger, unique=True, nullable=False, index=True)
    account_login = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False, default="User")  # User or Organization
    permissions = Column(JSON, nullable=True, default=dict)
    repository_selection = Column(String(50), nullable=False, default="all")  # all or selected
    suspended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    workspace = relationship("Workspace", back_populates="github_installations")
    repositories = relationship("Repository", back_populates="installation")

    def __repr__(self):
        return f"<GitHubAppInstallation {self.account_login} (ID: {self.installation_id})>"
