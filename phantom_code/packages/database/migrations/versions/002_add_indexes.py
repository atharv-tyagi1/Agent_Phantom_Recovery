"""add_indexes

Revision ID: 002
Revises: 001
Create Date: 2026-06-10 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # executions
    op.create_index('ix_executions_status', 'executions', ['status'], unique=False)
    
    # checkpoints
    op.create_index('ix_checkpoints_execution_id', 'checkpoints', ['execution_id'], unique=False)
    op.create_index('ix_checkpoints_created_at', 'checkpoints', ['created_at'], unique=False)
    
    # execution_states
    op.create_index('ix_execution_states_execution_id', 'execution_states', ['execution_id'], unique=False)
    
    # tasks
    op.create_index('ix_tasks_execution_id', 'tasks', ['execution_id'], unique=False)
    op.create_index('ix_tasks_status', 'tasks', ['status'], unique=False)

    # audit_logs
    op.create_index('ix_audit_logs_correlation_id', 'audit_logs', ['correlation_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_audit_logs_correlation_id', table_name='audit_logs')
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_index('ix_tasks_execution_id', table_name='tasks')
    op.drop_index('ix_execution_states_execution_id', table_name='execution_states')
    op.drop_index('ix_checkpoints_created_at', table_name='checkpoints')
    op.drop_index('ix_checkpoints_execution_id', table_name='checkpoints')
    op.drop_index('ix_executions_status', table_name='executions')
