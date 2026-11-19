import random
import time
from functools import wraps

from payment_gateway.audit_logger import log_payment
from payment_gateway.exceptions import (
    GatewayUnavailableError,
    PaymentError,
    PaymentTimeoutError,
)


def retry(
    func=None,
    *,
    attempts=3,
    initial_delay=1,
    backoff_factor=2,
    jitter=0.2,
):
    """Retry a function with exponential backoff and jitter."""

    if attempts < 1:
        raise ValueError("Attempts must be at least 1")

    if initial_delay < 0:
        raise ValueError("Initial delay cannot be negative")

    if backoff_factor < 1:
        raise ValueError("Backoff factor must be at least 1")

    if not 0 <= jitter <= 1:
        raise ValueError("Jitter must be between 0 and 1")

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):
            payment_id = kwargs.pop("_payment_id", None)
            gateway_name = kwargs.pop("_gateway_name", None)
            attempt_callback = kwargs.pop("_attempt_callback", None)

            for attempt in range(1, attempts + 1):
                try:
                    log_payment(
                        f"Attempt {attempt} started",
                        payment_id=payment_id,
                        gateway=gateway_name,
                    )

                    result = function(*args, **kwargs)

                except PaymentError as error:
                    if attempt_callback is not None:
                        attempt_callback(
                            attempt,
                            "FAILED",
                            str(error),
                        )

                    if not isinstance(
                        error,
                        (
                            PaymentTimeoutError,
                            GatewayUnavailableError,
                        ),
                    ):
                        raise

                    log_payment(
                        f"Attempt {attempt} failed: {error}",
                        payment_id=payment_id,
                        gateway=gateway_name,
                    )

                    if attempt == attempts:
                        log_payment(
                            f"All {attempts} attempts failed",
                            payment_id=payment_id,
                            gateway=gateway_name,
                        )
                        raise

                    delay = initial_delay * (backoff_factor ** (attempt - 1))

                    random_jitter = random.uniform(
                        0,
                        delay * jitter,
                    )

                    total_delay = delay + random_jitter

                    log_payment(
                        f"Retrying after {total_delay:.2f} seconds",
                        payment_id=payment_id,
                        gateway=gateway_name,
                    )

                    time.sleep(total_delay)

                else:
                    if attempt_callback is not None:
                        attempt_callback(
                            attempt,
                            "SUCCESS",
                            result.message,
                        )

                    log_payment(
                        f"Attempt {attempt} successful",
                        payment_id=payment_id,
                        gateway=gateway_name,
                    )

                    return result

        return wrapper

    if func is not None:
        return decorator(func)

    return decorator
