import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from db.session import Base


class ProjectMemory(Base):
    """
    Persistent, structured facts about a specific project.
    Stores key-value pairs that the agent learns over time:
    e.g. "primary_language: Python", "test_runner: pytest", "entry_point: src/main.py"
    """
    __tablename__ = "project_memory"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    context = Column(JSON, nullable=True, default=dict)  # optional metadata about this fact
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    project = relationship("Project", backref="memory_facts")

    # Unique constraint: one value per key per project
    __table_args__ = (
        Index("ix_project_memory_project_id", "project_id"),
        Index("ix_project_memory_key", "project_id", "key", unique=True),
    )

    def __repr__(self):
        return f"<ProjectMemory project={self.project_id} {self.key}={self.value!r}>"


class ExperienceMemory(Base):
    """
    Global cross-project experience store. The agent accumulates reusable
    problem-solution pairs here to avoid re-solving known issues.
    e.g. A fix for a circular import pattern, a recurring SQLAlchemy pitfall, etc.
    """
    __tablename__ = "experience_memory"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tags = Column(JSON, nullable=False, default=list)    # List[str] — for tag-based retrieval
    problem = Column(Text, nullable=False)               # Description of the problem
    solution = Column(Text, nullable=False)              # How it was solved
    source_project_id = Column(String, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    source_execution_id = Column(String, ForeignKey("executions.id", ondelete="SET NULL"), nullable=True)
    relevance_score = Column(String, nullable=True)      # optional score for future ranking
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_experience_memory_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<ExperienceMemory tags={self.tags} problem={self.problem[:40]!r}>"
