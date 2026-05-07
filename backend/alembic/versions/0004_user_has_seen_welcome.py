"""Add has_seen_welcome to user

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-07
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # server_default=true so existing rows are treated as already welcomed
    # (they signed up before this feature existed)
    op.add_column(
        "user",
        sa.Column(
            "has_seen_welcome",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade() -> None:
    op.drop_column("user", "has_seen_welcome")
