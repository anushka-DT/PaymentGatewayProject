import pytest

from payment_gateway.exceptions import PaymentTimeoutError
from payment_gateway.retry import retry


def test_retry_uses_configured_attempts(monkeypatch):
    attempts = []

    monkeypatch.setattr(
        "payment_gateway.retry.time.sleep",
        lambda delay: None,
    )
    monkeypatch.setattr(
        "payment_gateway.retry.random.uniform",
        lambda lower, upper: 0,
    )

    @retry(attempts=2, initial_delay=1)
    def failing_function():
        attempts.append(1)
        raise PaymentTimeoutError("Temporary timeout")

    with pytest.raises(PaymentTimeoutError):
        failing_function()

    assert len(attempts) == 2


def test_retry_uses_exponential_backoff(monkeypatch):
    delays = []
    attempts = []

    monkeypatch.setattr(
        "payment_gateway.retry.time.sleep",
        delays.append,
    )
    monkeypatch.setattr(
        "payment_gateway.retry.random.uniform",
        lambda lower, upper: 0,
    )

    @retry(
        attempts=3,
        initial_delay=1,
        backoff_factor=2,
        jitter=0,
    )
    def failing_function():
        attempts.append(1)
        raise PaymentTimeoutError("Temporary timeout")

    with pytest.raises(PaymentTimeoutError):
        failing_function()

    assert len(attempts) == 3
    assert delays == [1, 2]


def test_retry_does_not_retry_unexpected_exceptions():
    attempts = []

    @retry(attempts=3)
    def failing_function():
        attempts.append(1)
        raise ValueError("Unexpected error")

    with pytest.raises(ValueError):
        failing_function()

    assert len(attempts) == 1


def test_retry_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        retry(attempts=0)

    with pytest.raises(ValueError):
        retry(initial_delay=-1)

    with pytest.raises(ValueError):
        retry(backoff_factor=0)

    with pytest.raises(ValueError):
        retry(jitter=1.5)
