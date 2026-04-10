"""Initial config table

Revision ID: 001
Revises:
Create Date: 2026-04-10
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "config",
        sa.Column("key", sa.String, primary_key=True),
        sa.Column("value", sa.String),
    )


def downgrade():
    op.drop_table("config")
