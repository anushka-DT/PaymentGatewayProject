from decimal import Decimal
from unittest.mock import Mock

import pytest

from payment_gateway.client import PaymentGatewayClient
from payment_gateway.exceptions import (
    AllGatewaysFailedError,
    DuplicatePaymentError,
    PaymentError,
    PaymentFailedError,
    PaymentTimeoutError,
)
from payment_gateway.gateways import GatewayA, GatewayB
from payment_gateway.models import Payment, PaymentResponse


class AlwaysFailGateway:
    """A gateway that always raises a timeout."""

    def process_payment(self, payment):
        raise PaymentTimeoutError("Gateway failed")


@pytest.fixture
def payment():
    """Provide a sample payment."""

    return Payment(
        payment_id="PAY001",
        amount=Decimal("1500.00"),
        currency="INR",
        gateway="gateway_a",
    )


@pytest.fixture
def disable_retry_delay(monkeypatch):
    """Prevent actual waiting during retry tests."""

    monkeypatch.setattr(
        "payment_gateway.retry.time.sleep",
        lambda delay: None,
    )
    monkeypatch.setattr(
        "payment_gateway.retry.random.uniform",
        lambda a, b: 0,
    )


def make_payment(**overrides):
    """Create a payment with optional overridden values."""

    values = {
        "payment_id": "PAY001",
        "amount": Decimal("1500.00"),
        "currency": "INR",
        "gateway": "gateway_a",
    }
    values.update(overrides)

    return Payment(**values)


def test_primary_gateway_success(payment, payment_repository):
    gateways = {
        "gateway_a": GatewayA(),
        "gateway_b": GatewayB(),
    }

    client = PaymentGatewayClient(gateways, payment_repository)

    result = client.process_payment(payment)

    saved_payment = payment_repository.get_payment("PAY001")

    assert result.status == "SUCCESS"
    assert saved_payment.gateway == "gateway_a"
    assert saved_payment.status == "SUCCESS"


def test_fallback_gateway_success(
    payment,
    payment_repository,
    disable_retry_delay,
):
    gateway_a = GatewayA(fail_attempts=3)

    gateways = {
        "gateway_a": gateway_a,
        "gateway_b": GatewayB(),
    }

    client = PaymentGatewayClient(gateways, payment_repository)

    result = client.process_payment(payment)

    saved_payment = payment_repository.get_payment("PAY001")

    assert gateway_a.attempts == 3
    assert result.status == "SUCCESS"
    assert saved_payment.gateway == "gateway_b"
    assert saved_payment.status == "SUCCESS"


def test_all_gateways_fail(
    payment,
    payment_repository,
    disable_retry_delay,
):
    gateways = {
        "gateway_a": GatewayA(fail_attempts=3),
        "gateway_b": AlwaysFailGateway(),
    }

    client = PaymentGatewayClient(gateways, payment_repository)

    with pytest.raises(AllGatewaysFailedError) as error:
        client.process_payment(payment)

    saved_payment = payment_repository.get_payment("PAY001")

    assert len(error.value.failures) == 2
    assert saved_payment.status == "FAILED"
    assert saved_payment.gateway == "gateway_b"


@pytest.mark.parametrize(
    "amount",
    [
        Decimal(0),
        Decimal(-100),
        Decimal("-500.50"),
        Decimal("NaN"),
        Decimal("Infinity"),
    ],
)
def test_invalid_payment_amount(amount):
    with pytest.raises(PaymentError):
        make_payment(amount=amount)


def test_payment_amount_must_be_decimal():
    with pytest.raises(PaymentError, match="Decimal"):
        make_payment(amount=1500.00)


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("10.123"),
        Decimal("1500.999"),
        Decimal("0.001"),
    ],
)
def test_payment_amount_cannot_have_more_than_two_decimal_places(amount):
    with pytest.raises(PaymentError, match="2 decimal places"):
        make_payment(amount=amount)


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("100000000.00"),
        Decimal("9999999999.99"),
    ],
)
def test_payment_amount_cannot_exceed_maximum(amount):
    with pytest.raises(PaymentError, match="99999999.99"):
        make_payment(amount=amount)


def test_payment_amount_at_maximum_is_valid():
    payment = make_payment(amount=Decimal("99999999.99"))

    assert payment.amount == Decimal("99999999.99")


def test_valid_payment_amount_with_two_decimal_places():
    payment = make_payment(amount=Decimal("10.50"))

    assert payment.amount == Decimal("10.50")


@pytest.mark.parametrize(
    "currency",
    [
        "",
        "IN",
        "INR1",
        "inr",
        "12A",
    ],
)
def test_invalid_currency(currency):
    with pytest.raises(PaymentError):
        make_payment(currency=currency)


@pytest.mark.parametrize(
    "payment_id",
    [
        "",
        " ",
        "P" * 51,
    ],
)
def test_invalid_payment_id(payment_id):
    with pytest.raises(PaymentError):
        make_payment(payment_id=payment_id)


def test_invalid_gateway(payment, payment_repository):
    payment.gateway = "unknown_gateway"

    client = PaymentGatewayClient(
        {"gateway_a": GatewayA()},
        payment_repository,
    )

    with pytest.raises(PaymentError, match="Invalid payment gateway"):
        client.process_payment(payment)

    assert payment_repository.get_payment("PAY001") is None


def test_duplicate_payment_id(payment, payment_repository):
    payment_repository.create_pending_payment(payment)

    client = PaymentGatewayClient(
        {"gateway_a": GatewayA()},
        payment_repository,
    )

    with pytest.raises(DuplicatePaymentError):
        client.process_payment(payment)


def test_gateway_response_with_wrong_payment_id(
    payment,
    payment_repository,
):
    mock_gateway = Mock()

    mock_gateway.process_payment.return_value = PaymentResponse(
        payment_id="OTHER001",
        status="SUCCESS",
        message="Mock payment successful",
    )

    client = PaymentGatewayClient(
        {"gateway_a": mock_gateway},
        payment_repository,
    )

    with pytest.raises(
        PaymentError,
        match="different payment",
    ):
        client.process_payment(payment)

    saved_payment = payment_repository.get_payment("PAY001")

    assert saved_payment.status == "FAILED"
    mock_gateway.process_payment.assert_called_once_with(payment)


@pytest.mark.parametrize(
    "invalid_response",
    [
        None,
        "SUCCESS",
        {},
        {"payment_id": "PAY001"},
    ],
)
def test_gateway_response_must_be_payment_response(
    payment,
    payment_repository,
    invalid_response,
):
    mock_gateway = Mock()
    mock_gateway.process_payment.return_value = invalid_response

    client = PaymentGatewayClient(
        {"gateway_a": mock_gateway},
        payment_repository,
    )

    with pytest.raises(
        PaymentError,
        match="invalid payment response",
    ):
        client.process_payment(payment)

    saved_payment = payment_repository.get_payment("PAY001")

    assert saved_payment.status == "FAILED"
    mock_gateway.process_payment.assert_called_once_with(payment)


def test_gateway_response_with_invalid_status(payment, payment_repository):
    mock_gateway = Mock()

    mock_gateway.process_payment.return_value = PaymentResponse(
        payment_id="PAY001",
        status="UNKNOWN",
        message="Invalid status",
    )

    client = PaymentGatewayClient(
        {"gateway_a": mock_gateway},
        payment_repository,
    )

    with pytest.raises(PaymentError, match="invalid payment status"):
        client.process_payment(payment)

    saved_payment = payment_repository.get_payment("PAY001")

    assert saved_payment.status == "FAILED"


def test_gateway_declined_payment(payment, payment_repository):
    mock_gateway = Mock()

    mock_gateway.process_payment.return_value = PaymentResponse(
        payment_id="PAY001",
        status="FAILED",
        message="Payment declined",
    )

    client = PaymentGatewayClient(
        {"gateway_a": mock_gateway},
        payment_repository,
    )

    with pytest.raises(PaymentFailedError, match="Payment declined"):
        client.process_payment(payment)

    saved_payment = payment_repository.get_payment("PAY001")

    assert saved_payment.status == "FAILED"


def test_mock_gateway(payment, payment_repository):
    mock_gateway = Mock()

    mock_gateway.process_payment.return_value = PaymentResponse(
        payment_id="PAY001",
        status="SUCCESS",
        message="Mock payment successful",
    )

    client = PaymentGatewayClient(
        {"gateway_a": mock_gateway},
        payment_repository,
    )

    result = client.process_payment(payment)

    assert result.status == "SUCCESS"
    assert result.message == "Mock payment successful"

    mock_gateway.process_payment.assert_called_once_with(payment)


def test_client_without_database(payment):
    mock_gateway = Mock()

    mock_gateway.process_payment.return_value = PaymentResponse(
        payment_id="PAY001",
        status="SUCCESS",
        message="Payment successful",
    )

    client = PaymentGatewayClient({"gateway_a": mock_gateway})

    result = client.process_payment(payment)

    assert result.status == "SUCCESS"


def test_mutated_payment_is_revalidated_before_processing():
    from decimal import Decimal

    import pytest

    from payment_gateway.exceptions import PaymentError
    from payment_gateway.models import Payment

    payment = Payment(
        payment_id="PAY-MUTATED",
        amount=Decimal("100.00"),
        currency="INR",
        gateway="gateway_a",
    )

    payment.amount = Decimal("-100.00")

    client = PaymentGatewayClient({"gateway_a": GatewayA()})

    with pytest.raises(PaymentError):
        client.process_payment(payment)


def test_client_uses_configured_retry_attempts(payment):
    gateway_a = GatewayA(fail_attempts=3)

    client = PaymentGatewayClient(
        {"gateway_a": gateway_a},
        retry_attempts=4,
        retry_initial_delay=0,
    )

    result = client.process_payment(payment)

    assert result.status == "SUCCESS"
    assert gateway_a.attempts == 4


def test_gateway_attempt_history_with_fallback(
    payment,
    payment_repository,
    disable_retry_delay,
):
    gateway_a = GatewayA(fail_attempts=3)
    gateway_b = GatewayB()

    client = PaymentGatewayClient(
        {
            "gateway_a": gateway_a,
            "gateway_b": gateway_b,
        },
        payment_repository,
    )

    result = client.process_payment(payment)

    attempts = payment_repository.get_attempts("PAY001")

    assert result.status == "SUCCESS"
    assert len(attempts) == 4

    assert [
        (attempt.gateway, attempt.attempt_number, attempt.status)
        for attempt in attempts
    ] == [
        ("gateway_a", 1, "FAILED"),
        ("gateway_a", 2, "FAILED"),
        ("gateway_a", 3, "FAILED"),
        ("gateway_b", 1, "SUCCESS"),
    ]


def test_gateway_attempt_history_for_successful_primary(
    payment,
    payment_repository,
):
    client = PaymentGatewayClient(
        {"gateway_a": GatewayA()},
        payment_repository,
    )

    client.process_payment(payment)

    attempts = payment_repository.get_attempts("PAY001")

    assert len(attempts) == 1
    assert attempts[0].gateway == "gateway_a"
    assert attempts[0].attempt_number == 1
    assert attempts[0].status == "SUCCESS"
