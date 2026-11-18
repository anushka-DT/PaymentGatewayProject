import logging
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/payment_audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def log_payment(message):
    logger.info(message)
