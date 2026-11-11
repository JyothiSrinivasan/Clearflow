
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv(
    "PAYPAL_BASE_URL",
    "https://api-m.sandbox.paypal.com"
).rstrip("/")

CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")


def get_access_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("Missing PayPal Sandbox credentials")

    response = requests.post(
        f"{BASE_URL}/v1/oauth2/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        timeout=20
    )
    response.raise_for_status()
    return response.json()["access_token"]


def paypal_headers():
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }


def create_order(amount):
    response = requests.post(
        f"{BASE_URL}/v2/checkout/orders",
        headers=paypal_headers(),
        json={
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "USD",
                    "value": f"{amount:.2f}"
                },
                "description": "Clearflow Sandbox Payment"
            }],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "return_url": "http://127.0.0.1:8400",
                        "cancel_url": "http://127.0.0.1:8400",
                        "user_action": "PAY_NOW"
                    }
                }
            }
        },
        timeout=20
    )
    response.raise_for_status()

    data = response.json()
    approval_url = next(
        (
            link["href"]
            for link in data.get("links", [])
            if link.get("rel") in ("payer-action", "approve")
        ),
        None
    )

    return data["id"], approval_url


def get_order(order_id):
    response = requests.get(
        f"{BASE_URL}/v2/checkout/orders/{order_id}",
        headers=paypal_headers(),
        timeout=20
    )
    response.raise_for_status()
    return response.json()


def capture_order(order_id):
    response = requests.post(
        f"{BASE_URL}/v2/checkout/orders/{order_id}/capture",
        headers=paypal_headers(),
        timeout=20
    )
    response.raise_for_status()
    return response.json()
