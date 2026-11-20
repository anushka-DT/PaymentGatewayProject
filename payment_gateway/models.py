from dataclasses import dataclass
from decimal import Decimal

from payment_gateway.exceptions import PaymentError


@dataclass
class Payment:
    payment_id: str
    amount: Decimal
    currency: str
    gateway: str

    def __post_init__(self):
        """Validate payment details when a Payment is created."""

        self.validate()

    def validate(self):
        """Validate payment details before processing."""

        if not isinstance(self.payment_id, str) or not self.payment_id.strip():
            raise PaymentError("Payment ID is required")

        if len(self.payment_id) > 50:
            raise PaymentError("Payment ID cannot exceed 50 characters")

        if not isinstance(self.amount, Decimal):
            raise PaymentError("Payment amount must be a Decimal value")

        if not self.amount.is_finite() or self.amount <= 0:
            raise PaymentError("Payment amount must be greater than zero")

        if self.amount.as_tuple().exponent < -2:
            raise PaymentError("Payment amount cannot have more than 2 decimal places")

        if self.amount > Decimal("99999999.99"):
            raise PaymentError("Payment amount cannot exceed 99999999.99")

        if (
            not isinstance(self.currency, str)
            or len(self.currency) != 3
            or not self.currency.isascii()
            or not self.currency.isalpha()
            or not self.currency.isupper()
        ):
            raise PaymentError("Currency must be a 3-letter uppercase code")

        if not isinstance(self.gateway, str) or not self.gateway.strip():
            raise PaymentError("Payment gateway is required")


@dataclass
class PaymentResponse:
    payment_id: str
    status: str
    message: str
