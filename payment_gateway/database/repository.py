from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from payment_gateway.database.db_models import (
    PaymentAttemptRecord,
    PaymentRecord,
)
from payment_gateway.exceptions import DuplicatePaymentError


class PaymentRepository:
    """Handles database operations for payment records."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create_pending_payment(self, payment):
        """Create a pending record before gateway processing."""

        try:
            with self.session_factory.begin() as session:
                existing = session.get(
                    PaymentRecord,
                    payment.payment_id,
                )

                if existing is not None:
                    raise DuplicatePaymentError(
                        f"Payment ID already exists: {payment.payment_id}"
                    )

                record = PaymentRecord(
                    payment_id=payment.payment_id,
                    amount=payment.amount,
                    currency=payment.currency,
                    gateway=payment.gateway,
                    status="PENDING",
                    message="Payment processing started",
                )

                session.add(record)

        except IntegrityError as error:
            if self.get_payment(payment.payment_id) is not None:
                raise DuplicatePaymentError(
                    f"Payment ID already exists: {payment.payment_id}"
                ) from error

            raise

    def create_attempt(
        self,
        payment_id,
        gateway,
        attempt_number,
        status,
        message,
    ):
        """Store the result of an individual gateway attempt."""

        with self.session_factory.begin() as session:
            attempt = PaymentAttemptRecord(
                payment_id=payment_id,
                gateway=gateway,
                attempt_number=attempt_number,
                status=status,
                message=message,
            )

            session.add(attempt)

    def get_attempts(self, payment_id):
        """Retrieve all gateway attempts for a payment."""

        statement = (
            select(PaymentAttemptRecord)
            .where(PaymentAttemptRecord.payment_id == payment_id)
            .order_by(PaymentAttemptRecord.id)
        )

        with self.session_factory() as session:
            return list(session.scalars(statement).all())

    def get_payment(self, payment_id):
        """Retrieve a payment using its ID."""

        with self.session_factory() as session:
            return session.get(PaymentRecord, payment_id)

    def get_all_payments(self):
        """Retrieve all payments, newest first."""

        statement = select(PaymentRecord).order_by(PaymentRecord.created_at.desc())

        with self.session_factory() as session:
            return list(session.scalars(statement).all())

    def update_status(
        self,
        payment_id,
        status,
        message,
        gateway_name=None,
    ):
        """Update the status, message, and gateway of a payment."""

        with self.session_factory.begin() as session:
            record = session.get(PaymentRecord, payment_id)

            if record is None:
                return False

            record.status = status
            record.message = message

            if gateway_name is not None:
                record.gateway = gateway_name

            return True
