from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""


class PaymentRecord(Base):
    """Database model for storing payment records."""

    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'SUCCESS', 'FAILED')",
            name="check_payment_status",
        ),
    )

    payment_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    gateway: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class PaymentAttemptRecord(Base):
    """Database model for storing individual gateway attempts."""

    __tablename__ = "payment_attempts"

    __table_args__ = (
        CheckConstraint(
            "status IN ('SUCCESS', 'FAILED')",
            name="check_attempt_status",
        ),
        UniqueConstraint(
            "payment_id",
            "gateway",
            "attempt_number",
            name="unique_payment_gateway_attempt",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    payment_id: Mapped[str] = mapped_column(
        ForeignKey("payments.payment_id"),
        nullable=False,
    )

    gateway: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    attempt_number: Mapped[int] = mapped_column(
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
