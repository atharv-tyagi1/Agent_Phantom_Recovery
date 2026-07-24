import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, BigInteger, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from db.session import Base


class GitHubOAuthAccount(Base):
    """
    Stores user GitHub OAuth credentials for identity management.
    OAuth access tokens are encrypted at rest using AES-256 (Fernet).
    """
    __tablename__ = "github_oauth_accounts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    github_user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    github_username = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    access_token_encrypted = Column(Text, nullable=False)
    scopes = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", backref="github_oauth_account")

    def __repr__(self):
        return f"<GitHubOAuthAccount {self.github_username} (User ID: {self.user_id})>"
