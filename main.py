"""Main entry point for the payment gateway application."""

from decimal import Decimal

from payment_gateway.audit_logger import configure_logging
from payment_gateway.client import PaymentGatewayClient
from payment_gateway.database.connection import create_database
from payment_gateway.database.repository import PaymentRepository
from payment_gateway.exceptions import PaymentError
from payment_gateway.gateways import GatewayA, GatewayB
from payment_gateway.models import Payment


def main():
    """Set up the application and process a sample payment."""

    configure_logging()

    engine, session_factory = create_database()

    try:
        payment_repository = PaymentRepository(session_factory)

        gateways = {
            "gateway_a": GatewayA(fail_attempts=3),
            "gateway_b": GatewayB(),
        }

        client = PaymentGatewayClient(
            gateways,
            payment_repository=payment_repository,
        )

        payment = Payment(
            payment_id="Test_Payment",
            amount=Decimal("1500.00"),
            currency="INR",
            gateway="gateway_a",
        )

        try:
            result = client.process_payment(payment)
            print(result.message)

        except PaymentError as error:
            print("Payment failed:", error)

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
