
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api-m.sandbox.paypal.com"
CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")

# Replace with the order ID from your terminal

ORDER_ID = "8XX37572RY993415T"


token_response = requests.post(
    f"{BASE_URL}/v1/oauth2/token",
    auth=(CLIENT_ID, CLIENT_SECRET),
    data={"grant_type": "client_credentials"},
    timeout=20
)
token_response.raise_for_status()

access_token = token_response.json()["access_token"]

capture_response = requests.post(
    f"{BASE_URL}/v2/checkout/orders/{ORDER_ID}/capture",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    timeout=20
)

if capture_response.ok:
    data = capture_response.json()

    print("Order status:", data.get("status"))

    for unit in data.get("purchase_units", []):
        captures = unit.get("payments", {}).get("captures", [])
        for capture in captures:
            print("Capture ID:", capture.get("id"))
            print("Capture status:", capture.get("status"))
            print("Amount:", capture.get("amount"))
else:
    print("Capture failed.")
    print("HTTP status:", capture_response.status_code)
    print("Error details:", capture_response.text)
