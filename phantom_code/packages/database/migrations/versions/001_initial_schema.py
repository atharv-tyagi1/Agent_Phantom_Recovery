"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-06-10 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('executions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('goal', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('event_version', sa.String(), nullable=False),
        sa.Column('correlation_id', sa.String(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('checkpoints',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('execution_id', sa.String(), nullable=True),
        sa.Column('agent_state', sa.JSON(), nullable=False),
        sa.Column('task_state', sa.JSON(), nullable=False),
        sa.Column('retrieved_context_ids', sa.JSON(), nullable=False),
        sa.Column('tool_outputs', sa.JSON(), nullable=False),
        sa.Column('decision_history', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['execution_id'], ['executions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('execution_states',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('execution_id', sa.String(), nullable=True),
        sa.Column('phase', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['execution_id'], ['executions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('execution_id', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['execution_id'], ['executions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('tasks')
    op.drop_table('execution_states')
    op.drop_table('checkpoints')
    op.drop_table('audit_logs')
    op.drop_table('executions')
