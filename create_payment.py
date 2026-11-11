
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api-m.sandbox.paypal.com"
CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Missing PayPal Sandbox credentials.")

# Step 1: Obtain OAuth token
token_response = requests.post(
    f"{BASE_URL}/v1/oauth2/token",
    auth=(CLIENT_ID, CLIENT_SECRET),
    data={"grant_type": "client_credentials"},
    timeout=20
)
token_response.raise_for_status()
access_token = token_response.json()["access_token"]

# Step 2: Create a PayPal order
order_response = requests.post(
    f"{BASE_URL}/v2/checkout/orders",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    json={
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": "1.00"
                },
                "description": "Clearflow Sandbox Test Payment"
            }
        ],
        "application_context": {
            "return_url": "http://localhost:8400",
            "cancel_url": "http://localhost:8400"
        }
    },
    timeout=20
)

if not order_response.ok:
    print("HTTP status:", order_response.status_code)
    print("Order creation failed.")
    raise SystemExit(1)

order = order_response.json()

print("SUCCESS: PayPal Sandbox order created!")
print("Order ID:", order["id"])
print("Status:", order["status"])

for link in order.get("links", []):
    if link["rel"] in ("approve", "payer-action"):
        print("Buyer approval URL:", link["href"])
