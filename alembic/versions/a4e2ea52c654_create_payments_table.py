"""create payments table

Revision ID: a4e2ea52c654
Revises:
Create Date: 2026-11-19 13:00:39.914523
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a4e2ea52c654"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the original payments table."""

    op.create_table(
        "payments",
        sa.Column(
            "payment_id",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "amount",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
        ),
        sa.Column(
            "gateway",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("payment_id"),
    )


def downgrade() -> None:
    """Remove the payments table."""

    op.drop_table("payments")
