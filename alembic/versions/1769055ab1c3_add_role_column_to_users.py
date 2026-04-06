"""add role column to users

Revision ID: 1769055ab1c3
Revises: None
Create Date: 2026-04-06
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "1769055ab1c3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
    )


def downgrade():
    op.drop_column("users", "role")
