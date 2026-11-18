
from decimal import Decimal

from payment_gateway.audit_logger import log_payment
from payment_gateway.exceptions import (
    GatewayUnavailableError,
    PaymentError,
    PaymentTimeoutError,
)
from payment_gateway.models import PaymentResponse
from payment_gateway.retry import retry


class PaymentGatewayClient:
    """Process payments using primary and fallback gateways."""

    def __init__(self, gateways, payment_repository=None):
        self.gateways = gateways
        self.payment_repository = payment_repository

    def _validate_payment(self, payment):
        """Check payment details before processing."""

        if not isinstance(payment.payment_id, str) or not payment.payment_id.strip():
            raise PaymentError("Payment ID is required")

        if len(payment.payment_id) > 50:
            raise PaymentError("Payment ID cannot exceed 50 characters")

        if not isinstance(payment.amount, Decimal):
            raise PaymentError("Payment amount must be a Decimal value")

        if not payment.amount.is_finite() or payment.amount <= 0:
            raise PaymentError("Payment amount must be greater than zero")

        if payment.amount.as_tuple().exponent < -2:
            raise PaymentError(
                "Payment amount cannot have more than 2 decimal places"
            )

        if payment.amount > Decimal("99999999.99"):
            raise PaymentError(
                "Payment amount cannot exceed 99999999.99"
            )

        if (
            not isinstance(payment.currency, str)
            or len(payment.currency) != 3
            or not payment.currency.isascii()
            or not payment.currency.isalpha()
            or not payment.currency.isupper()
        ):
            raise PaymentError("Currency must be a 3-letter uppercase code")

        if not isinstance(payment.gateway, str) or not payment.gateway.strip():
            raise PaymentError("Payment gateway is required")

    def _save_payment(self, payment, status, message, gateway_name):
        """Save payment details if database integration is enabled."""

        if self.payment_repository is not None:
            self.payment_repository.save_payment(
                payment,
                status,
                message,
                gateway_name,
            )

    @retry
    def _process_payment(self, gateway, payment):
        """Process payment and verify the gateway response."""

        result = gateway.process_payment(payment)

        if not isinstance(result, PaymentResponse):
            raise PaymentError(
                "Gateway returned an invalid payment response"
            )

        if result.payment_id != payment.payment_id:
            raise PaymentError(
                "Gateway returned a response for a different payment"
            )

        return result

    def process_payment(self, payment):
        """Process payment with fallback if the primary gateway fails."""

        self._validate_payment(payment)

        primary_gateway = self.gateways.get(payment.gateway)

        if primary_gateway is None:
            raise PaymentError("Invalid payment gateway")

        last_error = None
        last_gateway_name = payment.gateway

        try:
            log_payment(f"Starting payment through {payment.gateway}")

            result = self._process_payment(primary_gateway, payment)

            log_payment(result.message)

            self._save_payment(
                payment,
                result.status,
                result.message,
                payment.gateway,
            )

            return result

        except (PaymentTimeoutError, GatewayUnavailableError) as error:
            last_error = error
            log_payment(
                f"{payment.gateway} failed after retries. Switching gateway."
            )

        for gateway_name, gateway in self.gateways.items():
            if gateway_name == payment.gateway:
                continue

            last_gateway_name = gateway_name

            try:
                log_payment(f"Switching to {gateway_name}")

                result = self._process_payment(gateway, payment)

                log_payment(result.message)

                self._save_payment(
                    payment,
                    result.status,
                    result.message,
                    gateway_name,
                )

                return result

            except (PaymentTimeoutError, GatewayUnavailableError) as error:
                last_error = error
                log_payment(f"{gateway_name} failed after retries")

        log_payment("Payment failed on all available gateways")

        self._save_payment(
            payment,
            "FAILED",
            str(last_error),
            last_gateway_name,
        )

        raise last_error
