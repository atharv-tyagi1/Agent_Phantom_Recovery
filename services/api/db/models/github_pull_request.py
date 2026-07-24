import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from db.session import Base


class PRState(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class GitHubPullRequest(Base):
    """
    Tracks GitHub Pull Requests automatically opened by Agent Phantom.
    """
    __tablename__ = "github_pull_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = Column(String, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String, ForeignKey("executions.id", ondelete="SET NULL"), nullable=True, index=True)
    pr_number = Column(Integer, nullable=False, index=True)
    title = Column(String(512), nullable=False)
    body = Column(Text, nullable=True)
    head_branch = Column(String(255), nullable=False)
    base_branch = Column(String(255), nullable=False, default="main")
    state = Column(SQLEnum(PRState), nullable=False, default=PRState.OPEN)
    github_url = Column(String(1024), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    execution = relationship("Execution", backref="pull_request")

    def __repr__(self):
        return f"<GitHubPullRequest #{self.pr_number} {self.title[:30]} ({self.state.value})>"
