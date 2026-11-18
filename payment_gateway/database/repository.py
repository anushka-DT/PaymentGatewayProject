from payment_gateway.database.db_models import PaymentRecord

class PaymentRepository:
    """Handles database operations for payment records."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def save_payment(self, payment, status, message, gateway_name=None):
        """Save a new payment or update an existing payment."""

        with self.session_factory.begin() as session:
            record = session.get(PaymentRecord, payment.payment_id)

            if record is None:
                record = PaymentRecord(
                    payment_id=payment.payment_id,
                    amount=payment.amount,
                    currency=payment.currency,
                    gateway=gateway_name or payment.gateway,
                    status=status,
                    message=message,
                )

                session.add(record)

            else:
                record.amount = payment.amount
                record.currency = payment.currency
                record.gateway = gateway_name or payment.gateway
                record.status = status
                record.message = message

            return record

    def get_payment(self, payment_id):
        """Retrieve a payment using its ID."""

        with self.session_factory() as session:
            return session.get(PaymentRecord, payment_id)

    def get_all_payments(self):
        """Retrieve all payment records."""

        with self.session_factory() as session:
            return (
                session.query(PaymentRecord)
                .order_by(PaymentRecord.created_at.desc())
                .all()
            )

    def update_status(self, payment_id, status, message):
        """Update the status and message of a payment."""

        with self.session_factory.begin() as session:
            record = session.get(PaymentRecord, payment_id)

            if record is None:
                return False

            record.status = status
            record.message = message

            return True
