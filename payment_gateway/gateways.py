from abc import ABC, abstractmethod

from payment_gateway.audit_logger import log_payment
from payment_gateway.exceptions import PaymentTimeoutError
from payment_gateway.models import Payment, PaymentResponse


class PaymentGateway(ABC):
    """Base class for payment gateways."""

    @abstractmethod
    def process_payment(self, payment: Payment) -> PaymentResponse:
        """Process a payment through a gateway."""


class GatewayA(PaymentGateway):
    """Primary payment gateway."""

    def __init__(self, fail_attempts: int = 0):
        self.fail_attempts = fail_attempts
        self.attempts = 0

    def process_payment(self, payment: Payment) -> PaymentResponse:
        self.attempts += 1

        if self.attempts <= self.fail_attempts:
            log_payment(
                "Gateway A timed out",
                payment_id=payment.payment_id,
                gateway="gateway_a",
            )
            raise PaymentTimeoutError("Gateway A timed out")

        log_payment(
            "Payment processed through Gateway A",
            payment_id=payment.payment_id,
            gateway="gateway_a",
        )

        return PaymentResponse(
            payment_id=payment.payment_id,
            status="SUCCESS",
            message="Payment processed through Gateway A",
        )


class GatewayB(PaymentGateway):
    """Fallback payment gateway."""

    def process_payment(self, payment: Payment) -> PaymentResponse:
        log_payment(
            "Payment processed through Gateway B",
            payment_id=payment.payment_id,
            gateway="gateway_b",
        )

        return PaymentResponse(
            payment_id=payment.payment_id,
            status="SUCCESS",
            message="Payment processed through Gateway B",
        )
