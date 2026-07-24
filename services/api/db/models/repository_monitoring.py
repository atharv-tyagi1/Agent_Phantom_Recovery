import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base


class MonitoringMode(str, enum.Enum):
    MANUAL = "manual"                  # No automated trigger
    SUGGEST = "suggest"                # Scan commit & create suggestion report
    AUTO_INVESTIGATE = "auto_investigate" # Investigate & run verifier, no code edits
    AUTO_FIX = "auto_fix"              # Automatically apply code edits
    AUTO_PR = "auto_pr"                # Apply fix & automatically create Pull Request


class RepositoryMonitoringSettings(Base):
    """
    Configures repository automation & monitoring triggers per repository.
    """
    __tablename__ = "repository_monitoring_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = Column(String, ForeignKey("repositories.id", ondelete="CASCADE"), unique=True, nullable=False)
    mode = Column(SQLEnum(MonitoringMode), nullable=False, default=MonitoringMode.AUTO_INVESTIGATE)
    trigger_on_push = Column(Boolean, nullable=False, default=True)
    trigger_on_pr = Column(Boolean, nullable=False, default=True)
    trigger_on_merge = Column(Boolean, nullable=False, default=True)
    branch_filter = Column(JSON, nullable=False, default=lambda: ["main", "master", "develop"])
    path_filter = Column(JSON, nullable=True, default=list)  # Optional path whitelist/blacklist
    file_extensions = Column(JSON, nullable=False, default=lambda: [".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java"])
    max_executions_per_day = Column(Integer, nullable=False, default=20)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    repository = relationship("Repository", back_populates="monitoring_settings")

    def __repr__(self):
        return f"<RepositoryMonitoringSettings repo={self.repository_id} mode={self.mode.value}>"
