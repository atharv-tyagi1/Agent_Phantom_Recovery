import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, BigInteger, JSON, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base


class GitHubCheckRun(Base):
    """
    Tracks GitHub Check Runs submitted during autonomous verification.
    """
    __tablename__ = "github_check_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = Column(String, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String, ForeignKey("executions.id", ondelete="SET NULL"), nullable=True, index=True)
    check_run_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(255), nullable=False, default="Agent Phantom Verification")
    status = Column(String(50), nullable=False, default="queued")  # queued, in_progress, completed
    conclusion = Column(String(50), nullable=True)  # success, failure, neutral, action_required
    head_sha = Column(String(100), nullable=False)
    output = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    repository = relationship("Repository", back_populates="check_runs")
    execution = relationship("Execution", backref="check_run")

    def __repr__(self):
        return f"<GitHubCheckRun {self.name} for {self.head_sha[:7]} ({self.status})>"
