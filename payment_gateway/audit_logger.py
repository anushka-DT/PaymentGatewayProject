import logging
import os

logger = logging.getLogger(__name__)


def configure_logging():
    """Configure application logging when the application starts."""

    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        filename="logs/payment_audit.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )


def log_payment(message, payment_id=None, gateway=None):
    """Write a payment log with optional transaction context."""

    context = []

    if payment_id is not None:
        context.append(f"payment_id={payment_id}")

    if gateway is not None:
        context.append(f"gateway={gateway}")

    if context:
        message = f"[{', '.join(context)}] {message}"

    logger.info(message)
