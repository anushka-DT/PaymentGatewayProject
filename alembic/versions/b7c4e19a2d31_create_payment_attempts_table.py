"""create payment attempts table"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b7c4e19a2d31"
down_revision: str | Sequence[str] | None = "23d48dfed356"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the payment attempts table."""

    op.create_table(
        "payment_attempts",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "payment_id",
            sa.String(50),
            sa.ForeignKey("payments.payment_id"),
            nullable=False,
        ),
        sa.Column(
            "gateway",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "attempt_number",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(20),
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
        sa.CheckConstraint(
            "status IN ('SUCCESS', 'FAILED')",
            name="check_attempt_status",
        ),
        sa.UniqueConstraint(
            "payment_id",
            "gateway",
            "attempt_number",
            name="unique_payment_gateway_attempt",
        ),
    )


def downgrade() -> None:
    """Remove the payment attempts table."""

    op.drop_table("payment_attempts")
