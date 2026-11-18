from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Payment:
    payment_id: str
    amount: Decimal
    currency: str
    gateway: str


@dataclass
class PaymentResponse:
    payment_id: str
    status: str
    message: str
