
import os
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("PAYPAL_CLIENT_ID")
client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
base_url = os.getenv(
    "PAYPAL_BASE_URL",
    "https://api-m.sandbox.paypal.com"
)

if not client_id or not client_secret:
    raise RuntimeError("PayPal credentials are missing from .env")

response = requests.post(
    f"{base_url}/v1/oauth2/token",
    auth=(client_id, client_secret),
    data={"grant_type": "client_credentials"},
    timeout=20
)

if response.ok:
    print("SUCCESS: Clearflow connected to PayPal Sandbox!")
    print("OAuth access token received securely.")
else:
    print("Connection failed.")
    print("HTTP status:", response.status_code)
    print("Check your Sandbox credentials and network.")
