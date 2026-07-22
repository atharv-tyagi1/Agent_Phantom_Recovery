import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from db.session import Base


class CodeSymbol(Base):
    """
    Extracted AST symbol (class, function, method, interface) from a codebase repository.
    Used for high-signal code navigation and context building.
    """
    __tablename__ = "code_symbols"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = Column(String, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(1024), nullable=False)
    name = Column(String(255), nullable=False)
    symbol_type = Column(String(50), nullable=False)  # 'class', 'function', 'method', 'interface', 'variable'
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    docstring = Column(Text, nullable=True)
    signature = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    repository = relationship("Repository", backref="symbols")

    __table_args__ = (
        Index("ix_code_symbols_repo_file", "repository_id", "file_path"),
        Index("ix_code_symbols_repo_name", "repository_id", "name"),
    )

    def __repr__(self):
        return f"<CodeSymbol {self.symbol_type} {self.name} in {self.file_path}:{self.start_line}>"


class DependencyEdge(Base):
    """
    Directed relationship edge between two files/modules in a repository.
    Tracks imports and calls to compute impact radius when code changes.
    """
    __tablename__ = "dependency_edges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = Column(String, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    source_file = Column(String(1024), nullable=False)
    target_file = Column(String(1024), nullable=False)
    dependency_type = Column(String(50), nullable=False, default="import")  # 'import', 'call', 'inheritance'
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    repository = relationship("Repository", backref="dependency_edges")

    __table_args__ = (
        Index("ix_dependency_edges_source", "repository_id", "source_file"),
        Index("ix_dependency_edges_target", "repository_id", "target_file"),
    )

    def __repr__(self):
        return f"<DependencyEdge {self.source_file} --({self.dependency_type})--> {self.target_file}>"
