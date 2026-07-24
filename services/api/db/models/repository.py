import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    installation_id = Column(String, ForeignKey("github_app_installations.id", ondelete="SET NULL"), nullable=True, index=True)
    github_repo_id = Column(BigInteger, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(512), nullable=True)  # e.g., owner/repo
    git_url = Column(String(512), nullable=False)
    default_branch = Column(String(100), nullable=False, default="main")
    local_path = Column(String(512), nullable=True)
    clone_status = Column(String(50), nullable=False, default="pending")  # pending, cloned, failed
    last_commit_sha = Column(String(100), nullable=True)
    last_indexed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="repositories")
    installation = relationship("GitHubAppInstallation", back_populates="repositories")
    monitoring_settings = relationship("RepositoryMonitoringSettings", back_populates="repository", uselist=False, cascade="all, delete-orphan")
    sync_jobs = relationship("RepositorySyncJob", back_populates="repository", cascade="all, delete-orphan")
    pull_requests = relationship("GitHubPullRequest", back_populates="repository", cascade="all, delete-orphan")
    check_runs = relationship("GitHubCheckRun", back_populates="repository", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Repository {self.name} ({self.git_url})>"
