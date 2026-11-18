from abc import ABC, abstractmethod

from payment_gateway.exceptions import PaymentTimeoutError
from payment_gateway.models import Payment, PaymentResponse


class PaymentGateway(ABC):
    @abstractmethod
    def process_payment(self, payment: Payment) -> PaymentResponse:
        pass


class GatewayA(PaymentGateway):
    def __init__(self, fail_attempts=0):
        self.attempts = 0
        self.fail_attempts = fail_attempts

    def process_payment(self, payment: Payment) -> PaymentResponse:

        self.attempts += 1
        print(f"Gateway A - Attempt {self.attempts}")

        if self.attempts <= self.fail_attempts:
            raise PaymentTimeoutError("Gateway A timed out")

        return PaymentResponse(
            payment_id=payment.payment_id,
            status="SUCCESS",
            message="Payment processed through Gateway A",
        )


class GatewayB(PaymentGateway):
    def process_payment(self, payment: Payment) -> PaymentResponse:

        print("Gateway B - Processing payment")

        return PaymentResponse(
            payment_id=payment.payment_id,
            status="SUCCESS",
            message="Payment processed through Gateway B",
        )
