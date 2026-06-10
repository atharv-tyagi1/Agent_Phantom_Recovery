import uuid
from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey

Base = declarative_base()

class Execution(Base):
    __tablename__ = "executions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    goal = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Idle")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExecutionState(Base):
    __tablename__ = "execution_states"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey("executions.id"))
    phase = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Checkpoint(Base):
    __tablename__ = "checkpoints"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey("executions.id"))
    agent_state = Column(JSON, nullable=False)
    task_state = Column(JSON, nullable=False)
    retrieved_context_ids = Column(JSON, nullable=False)
    tool_outputs = Column(JSON, nullable=False)
    decision_history = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey("executions.id"))
    description = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String, nullable=False)
    event_version = Column(String, nullable=False)
    correlation_id = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
