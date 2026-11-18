from payment_gateway.audit_logger import log_payment
from payment_gateway.exceptions import (
    GatewayUnavailableError,
    InvalidPaymentAmountError,
    PaymentError,
    PaymentTimeoutError,
)
from payment_gateway.retry import retry


class PaymentGatewayClient:
    def __init__(self, gateways):
        self.gateways = gateways

    @retry
    def _process_payment(self, gateway, payment):
        return gateway.process_payment(payment)

    def process_payment(self, payment):

        # Validate payment amount
        if payment.amount <= 0:
            raise InvalidPaymentAmountError("Payment amount must be greater than zero")

        # Get primary gateway
        primary_gateway = self.gateways.get(payment.gateway)

        if primary_gateway is None:
            raise PaymentError("Invalid payment gateway")

        # Try primary gateway first
        try:
            log_payment(f"Starting payment through {payment.gateway}")

            result = self._process_payment(primary_gateway, payment)

            log_payment(result.message)
            return result

        except (PaymentTimeoutError, GatewayUnavailableError) as error:
            log_payment(f"{payment.gateway} failed after retries. Switching gateway.")

            last_error = error

        # Try alternative gateways
        for gateway_name, gateway in self.gateways.items():
            if gateway_name == payment.gateway:
                continue

            try:
                log_payment(f"Switching to {gateway_name}")

                result = self._process_payment(gateway, payment)

                log_payment(result.message)
                return result

            except (PaymentTimeoutError, GatewayUnavailableError) as error:
                last_error = error
                log_payment(f"{gateway_name} failed after retries")

        # All gateways failed
        log_payment("Payment failed on all available gateways")
        raise last_error
