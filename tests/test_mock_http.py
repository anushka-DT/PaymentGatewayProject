from unittest.mock import patch

import requests


def make_payment_request():
    """Send a payment request to an external API."""

    response = requests.post(
        "https://payment-api.example.com/pay",
        json={"amount": 1500},
        timeout=5,
    )

    return response.json()


@patch("requests.post")
def test_make_payment_request(mock_post):
    # Define a fake API response
    mock_post.return_value.json.return_value = {
        "status": "SUCCESS",
        "payment_id": "PAY001",
    }

    result = make_payment_request()

    assert result["status"] == "SUCCESS"
    assert result["payment_id"] == "PAY001"

    # Verify that the HTTP request was called
    mock_post.assert_called_once_with(
        "https://payment-api.example.com/pay",
        json={"amount": 1500},
        timeout=5,
    )
