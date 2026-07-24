"""Phase 11.1 Production Hardening Migration

Revision ID: 001_phase11_hardening
Revises: 
Create Date: 2026-07-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_phase11_hardening'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create workspace_invitations table
    op.create_table(
        'workspace_invitations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('invited_by_id', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index('ix_workspace_invitations_workspace_id', 'workspace_invitations', ['workspace_id'])
    op.create_index('ix_workspace_invitations_email', 'workspace_invitations', ['email'])

    # 2. Create workspace_audit_logs table
    op.create_table(
        'workspace_audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('actor_user_id', sa.String(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('target_resource', sa.String(length=255), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workspace_audit_logs_workspace_id', 'workspace_audit_logs', ['workspace_id'])
    op.create_index('ix_workspace_audit_logs_action', 'workspace_audit_logs', ['action'])


def downgrade() -> None:
    op.drop_index('ix_workspace_audit_logs_action', table_name='workspace_audit_logs')
    op.drop_index('ix_workspace_audit_logs_workspace_id', table_name='workspace_audit_logs')
    op.drop_table('workspace_audit_logs')

    op.drop_index('ix_workspace_invitations_email', table_name='workspace_invitations')
    op.drop_index('ix_workspace_invitations_workspace_id', table_name='workspace_invitations')
    op.drop_table('workspace_invitations')
