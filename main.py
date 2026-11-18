"""Main entry point for the payment gateway application."""
from payment_gateway.client import PaymentGatewayClient
from payment_gateway.exceptions import PaymentError
from payment_gateway.gateways import GatewayA, GatewayB
from payment_gateway.models import Payment

gateways = {"gateway_a": GatewayA(fail_attempts=3), "gateway_b": GatewayB()}

client = PaymentGatewayClient(gateways)

payment = Payment(
    payment_id="PAY001", amount=1500.00, currency="INR", gateway="gateway_a"
)

try:
    result = client.process_payment(payment)
    print(result.message)

except PaymentError as error:
    print("Payment failed:", error)
