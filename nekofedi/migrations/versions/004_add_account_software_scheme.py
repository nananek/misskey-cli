"""Add software and scheme columns to accounts

Revision ID: 004
Revises: 003
Create Date: 2026-04-10
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("accounts", sa.Column("software", sa.String, nullable=True))
    op.add_column("accounts", sa.Column("scheme", sa.String, nullable=True))


def downgrade():
    op.drop_column("accounts", "scheme")
    op.drop_column("accounts", "software")
