from payment_gateway.audit_logger import log_payment
from payment_gateway.exceptions import (
    AllGatewaysFailedError,
    GatewayUnavailableError,
    PaymentError,
    PaymentFailedError,
    PaymentTimeoutError,
)
from payment_gateway.models import PaymentResponse
from payment_gateway.retry import retry


class PaymentGatewayClient:
    """Process payments using primary and fallback gateways."""

    def __init__(
        self,
        gateways,
        payment_repository=None,
        *,
        retry_attempts=3,
        retry_initial_delay=1,
        retry_backoff_factor=2,
        retry_jitter=0.2,
    ):
        self.gateways = gateways
        self.payment_repository = payment_repository

        self._process_with_retry = retry(
            attempts=retry_attempts,
            initial_delay=retry_initial_delay,
            backoff_factor=retry_backoff_factor,
            jitter=retry_jitter,
        )(self._process_with_retry)

    def _process_payment(self, gateway, payment):
        """Process payment and validate the gateway response."""

        result = gateway.process_payment(payment)

        if not isinstance(result, PaymentResponse):
            raise PaymentError("Gateway returned an invalid payment response")

        if result.payment_id != payment.payment_id:
            raise PaymentError("Gateway returned a response for a different payment")

        if result.status not in ("SUCCESS", "FAILED"):
            raise PaymentError("Gateway returned an invalid payment status")

        if result.status == "FAILED":
            raise PaymentFailedError(result.message)

        return result

    def _process_with_retry(self, gateway, payment):
        """Process a payment with retry enabled."""

        return self._process_payment(gateway, payment)

    def _update_payment(self, payment, status, message, gateway_name):
        """Update the database record if database integration is enabled."""

        if self.payment_repository is not None:
            updated = self.payment_repository.update_status(
                payment.payment_id,
                status,
                message,
                gateway_name,
            )

            if not updated:
                raise PaymentError(f"Payment record not found: {payment.payment_id}")

    def process_payment(self, payment):
        """Process payment through primary and fallback gateways."""

        payment.validate()

        primary_gateway_name = payment.gateway
        primary_gateway = self.gateways.get(primary_gateway_name)

        if primary_gateway is None:
            raise PaymentError("Invalid payment gateway")

        if self.payment_repository is not None:
            self.payment_repository.create_pending_payment(payment)

        ordered_gateways = [
            (primary_gateway_name, primary_gateway),
            *(
                (name, gateway)
                for name, gateway in self.gateways.items()
                if name != primary_gateway_name
            ),
        ]

        failures = []
        current_gateway_name = primary_gateway_name

        try:
            log_payment(
                "Starting payment",
                payment_id=payment.payment_id,
                gateway=primary_gateway_name,
            )

            for index, (gateway_name, gateway) in enumerate(ordered_gateways):
                current_gateway_name = gateway_name

                if index > 0:
                    log_payment(
                        "Switching to fallback gateway",
                        payment_id=payment.payment_id,
                        gateway=gateway_name,
                    )

                attempt_callback = None

                if self.payment_repository is not None:

                    def attempt_callback(
                        attempt_number,
                        status,
                        message,
                        current_gateway=gateway_name,
                    ):
                        self.payment_repository.create_attempt(
                            payment.payment_id,
                            current_gateway,
                            attempt_number,
                            status,
                            message,
                        )

                try:
                    result = self._process_with_retry(
                        gateway,
                        payment,
                        _payment_id=payment.payment_id,
                        _gateway_name=gateway_name,
                        _attempt_callback=attempt_callback,
                    )

                    self._update_payment(
                        payment,
                        "SUCCESS",
                        result.message,
                        gateway_name,
                    )

                    log_payment(
                        result.message,
                        payment_id=payment.payment_id,
                        gateway=gateway_name,
                    )

                    return result

                except (
                    PaymentTimeoutError,
                    GatewayUnavailableError,
                ) as error:
                    failures.append((gateway_name, error))

                    log_payment(
                        f"Gateway failed after retries: {error}",
                        payment_id=payment.payment_id,
                        gateway=gateway_name,
                    )

            raise AllGatewaysFailedError(failures)

        except PaymentError as error:
            self._update_payment(
                payment,
                "FAILED",
                str(error),
                current_gateway_name,
            )

            log_payment(
                f"Payment failed: {error}",
                payment_id=payment.payment_id,
                gateway=current_gateway_name,
            )

            raise
