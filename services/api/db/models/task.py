import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssignedModel(str, enum.Enum):
    PLANNER = "planner"
    REASONER = "reasoner"
    VERIFIER = "verifier"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    priority = Column(SQLEnum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    assigned_model = Column(SQLEnum(AssignedModel), nullable=True)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    project = relationship("Project", back_populates="tasks")
    executions = relationship("Execution", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task {self.title[:40]} ({self.status.value})>"
