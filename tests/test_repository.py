from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from payment_gateway.models import Payment


def create_payment():
    """Create a sample payment for testing."""

    return Payment(
        payment_id="PAY001",
        amount=Decimal("1500.00"),
        currency="INR",
        gateway="gateway_a",
    )


def test_save_payment(payment_repository):
    payment = create_payment()

    payment_repository.save_payment(
        payment,
        "SUCCESS",
        "Payment successful",
        "gateway_b",
    )

    saved_payment = payment_repository.get_payment("PAY001")

    assert saved_payment is not None
    assert saved_payment.payment_id == "PAY001"
    assert saved_payment.amount == Decimal("1500.00")
    assert saved_payment.gateway == "gateway_b"
    assert saved_payment.status == "SUCCESS"


def test_get_all_payments(payment_repository):
    payment = create_payment()

    payment_repository.save_payment(
        payment,
        "SUCCESS",
        "Payment successful",
        "gateway_b",
    )

    payments = payment_repository.get_all_payments()

    assert len(payments) == 1
    assert payments[0].payment_id == "PAY001"


def test_update_status(payment_repository):
    payment = create_payment()

    payment_repository.save_payment(
        payment,
        "PENDING",
        "Payment pending",
        "gateway_a",
    )

    updated = payment_repository.update_status(
        "PAY001",
        "SUCCESS",
        "Payment successful",
    )

    saved_payment = payment_repository.get_payment("PAY001")

    assert updated is True
    assert saved_payment.status == "SUCCESS"
    assert saved_payment.message == "Payment successful"


def test_update_status_for_missing_payment(payment_repository):
    updated = payment_repository.update_status(
        "UNKNOWN",
        "SUCCESS",
        "Payment successful",
    )

    assert updated is False


def test_save_payment_updates_existing_record(payment_repository):
    payment = create_payment()

    payment_repository.save_payment(
        payment,
        "PENDING",
        "Payment is pending",
        "gateway_a",
    )

    payment_repository.save_payment(
        payment,
        "SUCCESS",
        "Payment completed",
        "gateway_b",
    )

    saved_payment = payment_repository.get_payment("PAY001")

    assert saved_payment.status == "SUCCESS"
    assert saved_payment.message == "Payment completed"
    assert saved_payment.gateway == "gateway_b"


def test_save_payment_rolls_back_on_database_error(payment_repository):
    payment = create_payment()

    # An amount of None violates the database NOT NULL constraint.
    payment.amount = None

    with pytest.raises(IntegrityError):
        payment_repository.save_payment(
            payment,
            "SUCCESS",
            "Payment successful",
            "gateway_a",
        )

    # The failed transaction must not leave a payment record.
    saved_payment = payment_repository.get_payment("PAY001")

    assert saved_payment is None
