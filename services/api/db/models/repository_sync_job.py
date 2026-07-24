import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from db.session import Base


class SyncJobType(str, enum.Enum):
    CLONE = "clone"
    PULL = "pull"
    INDEX = "index"
    INCREMENTAL_INDEX = "incremental_index"


class SyncJobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RepositorySyncJob(Base):
    """
    Tracks repository synchronization and incremental indexing jobs.
    """
    __tablename__ = "repository_sync_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = Column(String, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(SQLEnum(SyncJobType), nullable=False)
    status = Column(SQLEnum(SyncJobStatus), nullable=False, default=SyncJobStatus.QUEUED)
    commit_sha = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    repository = relationship("Repository", back_populates="sync_jobs")

    def __repr__(self):
        return f"<RepositorySyncJob {self.job_type.value} for {self.repository_id} ({self.status.value})>"
