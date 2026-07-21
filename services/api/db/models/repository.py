import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    git_url = Column(String(512), nullable=False)
    default_branch = Column(String(100), nullable=False, default="main")
    local_path = Column(String(512), nullable=True)
    last_indexed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="repositories")

    def __repr__(self):
        return f"<Repository {self.name} ({self.git_url})>"
