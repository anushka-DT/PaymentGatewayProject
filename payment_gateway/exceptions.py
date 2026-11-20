class PaymentError(Exception):
    """Base exception for payment-related errors."""


class PaymentTimeoutError(PaymentError):
    """Raised when a payment gateway times out."""


class PaymentFailedError(PaymentError):
    """Raised when a payment is declined or fails."""


class GatewayUnavailableError(PaymentError):
    """Raised when a payment gateway is unavailable."""


class DuplicatePaymentError(PaymentError):
    """Raised when a payment ID already exists."""


class AllGatewaysFailedError(PaymentError):
    """Raised when all available gateways fail."""

    def __init__(self, failures):
        self.failures = failures

        details = "; ".join(f"{gateway}: {error}" for gateway, error in failures)

        super().__init__(f"All payment gateways failed. {details}")
