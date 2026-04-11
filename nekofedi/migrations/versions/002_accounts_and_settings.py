"""Replace config KV table with accounts and settings tables

Revision ID: 002
Revises: 001
Create Date: 2026-04-10
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("host", sa.String, nullable=False),
        sa.Column("username", sa.String),
        sa.Column("token", sa.String, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, default=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("default_visibility", sa.String, nullable=False, server_default="public"),
    )

    # migrate data from old config table
    conn = op.get_bind()
    host = conn.execute(sa.text("SELECT value FROM config WHERE key = 'host'")).scalar()
    token = conn.execute(sa.text("SELECT value FROM config WHERE key = 'token'")).scalar()
    visibility = conn.execute(sa.text("SELECT value FROM config WHERE key = 'default_visibility'")).scalar()

    if host and token:
        conn.execute(
            sa.text("INSERT INTO accounts (host, token, active) VALUES (:host, :token, 1)"),
            {"host": host, "token": token},
        )
    conn.execute(
        sa.text("INSERT INTO settings (default_visibility) VALUES (:v)"),
        {"v": visibility or "public"},
    )

    op.drop_table("config")


def downgrade():
    op.create_table(
        "config",
        sa.Column("key", sa.String, primary_key=True),
        sa.Column("value", sa.String),
    )

    conn = op.get_bind()
    acct = conn.execute(sa.text("SELECT host, token FROM accounts WHERE active = 1")).first()
    if acct:
        conn.execute(sa.text("INSERT INTO config (key, value) VALUES ('host', :v)"), {"v": acct[0]})
        conn.execute(sa.text("INSERT INTO config (key, value) VALUES ('token', :v)"), {"v": acct[1]})
    vis = conn.execute(sa.text("SELECT default_visibility FROM settings")).scalar()
    if vis:
        conn.execute(sa.text("INSERT INTO config (key, value) VALUES ('default_visibility', :v)"), {"v": vis})

    op.drop_table("settings")
    op.drop_table("accounts")
