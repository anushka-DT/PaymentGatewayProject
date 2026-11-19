from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlalchemy.exc import IntegrityError

from payment_gateway.exceptions import DuplicatePaymentError
from payment_gateway.models import Payment


def create_payment():
    """Create a sample payment for testing."""

    return Payment(
        payment_id="PAY001",
        amount=Decimal("1500.00"),
        currency="INR",
        gateway="gateway_a",
    )


def test_create_pending_payment(payment_repository):
    payment = create_payment()

    payment_repository.create_pending_payment(payment)

    saved_payment = payment_repository.get_payment("PAY001")

    assert saved_payment is not None
    assert saved_payment.payment_id == "PAY001"
    assert saved_payment.amount == Decimal("1500.00")
    assert saved_payment.gateway == "gateway_a"
    assert saved_payment.status == "PENDING"
    assert saved_payment.message == "Payment processing started"


def test_duplicate_payment_id_is_rejected(payment_repository):
    payment = create_payment()

    payment_repository.create_pending_payment(payment)

    with pytest.raises(DuplicatePaymentError):
        payment_repository.create_pending_payment(payment)

    saved_payment = payment_repository.get_payment("PAY001")

    assert saved_payment.status == "PENDING"


def test_get_all_payments(payment_repository):
    payment_repository.create_pending_payment(create_payment())

    payments = payment_repository.get_all_payments()

    assert len(payments) == 1
    assert payments[0].payment_id == "PAY001"


def test_update_status(payment_repository):
    payment_repository.create_pending_payment(create_payment())

    updated = payment_repository.update_status(
        "PAY001",
        "SUCCESS",
        "Payment successful",
        "gateway_b",
    )

    saved_payment = payment_repository.get_payment("PAY001")

    assert updated is True
    assert saved_payment.status == "SUCCESS"
    assert saved_payment.message == "Payment successful"
    assert saved_payment.gateway == "gateway_b"


def test_update_status_for_missing_payment(payment_repository):
    updated = payment_repository.update_status(
        "UNKNOWN",
        "SUCCESS",
        "Payment successful",
    )

    assert updated is False


def test_create_pending_payment_rolls_back_on_database_error(
    payment_repository,
):
    invalid_payment = SimpleNamespace(
        payment_id="PAY002",
        amount=None,
        currency="INR",
        gateway="gateway_a",
    )

    with pytest.raises(IntegrityError):
        payment_repository.create_pending_payment(invalid_payment)

    assert payment_repository.get_payment("PAY002") is None


def test_database_rejects_invalid_status(payment_repository):
    payment_repository.create_pending_payment(create_payment())

    with pytest.raises(IntegrityError):
        payment_repository.update_status(
            "PAY001",
            "UNKNOWN",
            "Invalid status",
        )

    saved_payment = payment_repository.get_payment("PAY001")

    assert saved_payment.status == "PENDING"


def test_create_and_get_payment_attempt(payment_repository):
    payment_repository.create_pending_payment(create_payment())

    payment_repository.create_attempt(
        "PAY001",
        "gateway_a",
        1,
        "FAILED",
        "Gateway timed out",
    )

    attempts = payment_repository.get_attempts("PAY001")

    assert len(attempts) == 1
    assert attempts[0].payment_id == "PAY001"
    assert attempts[0].gateway == "gateway_a"
    assert attempts[0].attempt_number == 1
    assert attempts[0].status == "FAILED"
    assert attempts[0].message == "Gateway timed out"


def test_get_attempts_returns_empty_list_for_unknown_payment(
    payment_repository,
):
    assert payment_repository.get_attempts("UNKNOWN") == []
