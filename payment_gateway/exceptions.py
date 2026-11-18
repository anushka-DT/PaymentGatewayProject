class PaymentError(Exception):
    pass


class PaymentTimeoutError(PaymentError):
    pass


class PaymentFailedError(PaymentError):
    pass


class GatewayUnavailableError(PaymentError):
    pass


class InvalidPaymentAmountError(PaymentError):
    """Raised when the payment amount is invalid."""
