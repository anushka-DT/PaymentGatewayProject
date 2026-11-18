class PaymentError(Exception):
    pass


class PaymentTimeoutError(PaymentError):
    pass


class PaymentFailedError(PaymentError):
    pass


class GatewayUnavailableError(PaymentError):
    pass
