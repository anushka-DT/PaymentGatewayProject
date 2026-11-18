import random
import time
from functools import wraps

from payment_gateway.audit_logger import log_payment
from payment_gateway.exceptions import GatewayUnavailableError, PaymentTimeoutError


def retry(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        for attempt in range(1, 4):
            try:
                log_payment(f"Attempt {attempt} started")

                result = func(*args, **kwargs)

                log_payment(f"Attempt {attempt} successful")
                return result

            except (PaymentTimeoutError, GatewayUnavailableError) as error:
                log_payment(f"Attempt {attempt} failed: {error}")

                if attempt == 3:
                    log_payment("All three attempts failed")
                    raise

                delay = 2 ** (attempt - 1)
                jitter = random.uniform(0, delay * 0.2)

                total_delay = delay + jitter

                log_payment(f"Retrying after {total_delay:.2f} seconds")

                time.sleep(total_delay)

    return wrapper
