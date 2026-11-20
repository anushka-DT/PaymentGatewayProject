"""add updated_at and payment status constraint"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# Revision identifiers, used by Alembic.
revision: str = "23d48dfed356"
down_revision: str | Sequence[str] | None = "a4e2ea52c654"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add updated_at and restrict payment status values."""

    with op.batch_alter_table(
        "payments",
        recreate="always",
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            )
        )

        batch_op.create_check_constraint(
            "check_payment_status",
            "status IN ('PENDING', 'SUCCESS', 'FAILED')",
        )


def downgrade() -> None:
    """Remove the status constraint and updated_at column."""

    with op.batch_alter_table(
        "payments",
        recreate="always",
    ) as batch_op:
        batch_op.drop_constraint(
            "check_payment_status",
            type_="check",
        )

        batch_op.drop_column("updated_at")
