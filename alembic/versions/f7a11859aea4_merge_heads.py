"""merge heads

Revision ID: f7a11859aea4
Revises: 003, 1769055ab1c3
Create Date: 2026-04-06 21:01:38.629501

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "f7a11859aea4"
down_revision: Union[str, None] = ("003", "1769055ab1c3")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
