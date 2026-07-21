import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base


class ExecutionStatus(str, enum.Enum):
    IDLE = "idle"
    PLANNING = "planning"
    INVESTIGATING = "investigating"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


class Execution(Base):
    __tablename__ = "executions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    goal = Column(String(1000), nullable=False)
    status = Column(SQLEnum(ExecutionStatus), nullable=False, default=ExecutionStatus.IDLE)
    current_phase = Column(String(100), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    task = relationship("Task", back_populates="executions")
    project = relationship("Project", back_populates="executions")

    def __repr__(self):
        return f"<Execution {self.id[:8]} ({self.status.value})>"
