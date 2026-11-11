# Clearflow

**Your cash flow, clearly in view.**

### AI-Powered PayPal Payment Intelligence & Cash-Flow Forecasting

Clearflow is a FinTech prototype developed for the **PayPal AI Hackathon 2026**. It combines PayPal Sandbox payment processing, verified payment synchronization, local AI-powered financial analysis, and interactive cash-flow forecasting in a unified Streamlit dashboard.

The application uses a **Terracotta & Cream** interface to present financial information clearly and accessibly.

## Key Features

### 1. Financial Dashboard
- Track synthetic INR income, expenses, and net cash flow.
- Add and review financial transactions.
- Store records locally in SQLite.
- View recent financial activity and payment summaries.

### 2. PayPal Sandbox Integration
- Create PayPal Sandbox checkout orders.
- Approve and capture test payments.
- Retrieve existing orders using PayPal REST APIs.
- Synchronize verified payment information into SQLite.
- Track order IDs, capture IDs, payment statuses, amounts, and currencies.

### 3. AI Financial Copilot
- Uses the locally hosted **Ollama Qwen2.5 3B** language model.
- Analyzes synthetic INR financial records and synchronized PayPal Sandbox payments.
- Answers questions about payment activity, captured amounts, expenses, and cash flow.
- Provides contextual financial explanations.
- Maintains separation between INR ledger totals and USD Sandbox payments.

### 4. Cash-Flow Forecasting
- INR baseline forecasts based on synthetic financial transactions.
- Separate USD scenario forecasts using user-defined assumptions.
- Adjustable opening balances, forecast periods, expected receipts, and expenses.
- Interactive Plotly charts.

Forecasts are illustrative estimates, not guaranteed predictions or outputs from a trained PayPal transaction forecasting model.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Programming language | Python |
| Payment integration | PayPal Sandbox REST APIs |
| Database | SQLite |
| AI model | Ollama — Qwen2.5 3B |
| Charts | Plotly |
| API testing | Postman |
| Configuration | Python-dotenv |
| Version control | Git & GitHub |

## System Architecture

```text
                      Clearflow
                          |
                  Streamlit Dashboard
                          |
         +----------------+----------------+
         |                |                |
     INR Ledger       PayPal API       AI Copilot
         |                |                |
         |         Verified Orders         |
         |                |                |
         +------------- SQLite ------------+
                          |
                   Financial Context
                          |
                     Local Ollama
                          |
                   AI Explanations

             INR and USD Forecast Modules
                          |
                     Plotly Charts
```

## Getting Started

### Prerequisites

- Python 3.13 or a compatible Python version
- Git
- Ollama installed locally
- PayPal Developer Sandbox credentials
- Postman (optional, for API testing)

### 1. Clone the Repository

```bash
git clone https://github.com/JyothiSrinivasan/Clearflow.git
cd Clearflow
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure PayPal Sandbox

Copy `.env.example` to `.env`.

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your own PayPal Sandbox credentials:

```dotenv
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
```

Never commit `.env` or real credentials to GitHub.

### 5. Configure Ollama

Install the required model:

```bash
ollama pull qwen2.5:3b
```

Make sure Ollama is running locally.

Clearflow communicates with Ollama through:

`http://127.0.0.1:11434/api/chat`

### 6. Run Clearflow

```bash
python -m streamlit run app.py
```

Open the application at:

**http://127.0.0.1:8400**

The local address and port are configured in `.streamlit/config.toml`.

The AI Copilot requires Ollama to be running. PayPal payment functionality requires valid Sandbox credentials and an appropriate Sandbox account.

## Demonstration Workflow

1. Open the Clearflow financial dashboard.
2. Review or add synthetic INR transactions.
3. Create and approve a PayPal Sandbox checkout payment.
4. Capture the approved payment and synchronize its verified order information.
5. Ask the AI Copilot to explain the recorded financial activity.
6. Explore the INR baseline forecast and separate USD scenario forecast.
7. Review the Postman API verification tests.

## PayPal Sandbox API Testing with Postman

Clearflow includes a Postman collection for reproducing API authentication and payment-verification tests.

**Collection:** `Clearflow_Postman_Collection.json`

### Included API Requests

| Request | Purpose |
|---|---|
| `01 - PayPal OAuth Access Token` | Authenticate using PayPal Sandbox OAuth 2.0 |
| `02 - Retrieve PayPal Order` | Retrieve an existing Sandbox order and validate payment information |

### Automated Test Results

All six automated order-verification tests passed during local testing.

| Test | Result |
|---|---|
| Order retrieval returns HTTP 200 | Passed |
| PayPal order is completed | Passed |
| Payment capture is completed | Passed |
| Payment amount is $1.00 USD | Passed |
| Capture amount matches order amount | Passed |
| Gross amount minus PayPal fee equals net settlement | Passed |

**Result: 6/6 tests passed.**

### Example Sandbox Transaction

| Field | Value |
|---|---|
| Order status | COMPLETED |
| Capture status | COMPLETED |
| Gross amount | $1.00 USD |
| PayPal fee | $0.54 USD |
| Net settlement | $0.46 USD |

These values were returned by the PayPal Sandbox API for the demonstrated transaction.

### Reproducing the Postman Tests

1. Install Postman.
2. Import `Clearflow_Postman_Collection.json`.
3. Create a PayPal Sandbox REST application through the PayPal Developer Dashboard.
4. Open Postman Local Vault.
5. Add the secrets `paypal_client_id` and `paypal_client_secret`, using your own Sandbox credentials.
6. Enable Vault access for trusted collection scripts when prompted.
7. Run `01 - PayPal OAuth Access Token`.
8. Run `02 - Retrieve PayPal Order`.
9. Open the **Test Results** tab to review the automated assertions.

The second request obtains a temporary OAuth access token through its pre-request script.

**Note for judges:** The included order ID refers to a demonstration Sandbox payment. If using a different Sandbox merchant account, replace the order ID with one created under your own account. The automated assertions expect a completed $1.00 USD payment with a completed capture; use a matching test order or adjust the assertions accordingly.

The Postman tests validate API behavior and payment-data consistency. They do not constitute a comprehensive application security assessment.

## Security Practices

- PayPal API credentials are loaded from local environment variables.
- `.env` is excluded from Git tracking.
- `.env.example` contains placeholder values.
- Postman Local Vault stores credentials for API testing.
- The exported Postman collection references Vault secrets rather than embedding actual credentials.
- PayPal Sandbox is used instead of live payment processing.
- Synthetic INR ledger records and USD Sandbox payment records are maintained separately.
- Access tokens are obtained at runtime for authenticated API requests.

## Important Limitations

- PayPal transactions use Sandbox test funds only.
- INR financial records are synthetic demonstration data.
- PayPal synchronization retrieves known orders rather than automatically importing complete account transaction history.
- USD payments are not silently converted or included in INR totals.
- USD forecasts use manually entered scenario assumptions.
- Forecasts are illustrative, not guaranteed financial predictions.
- The AI Copilot provides informational explanations rather than regulated financial advice.
- The complete workflow requires local Ollama setup and PayPal Sandbox credentials.
- The application runs locally by default and is not presented as a publicly hosted service.

## Hackathon Demo

**Demo video:** To be added after recording.

The demonstration will cover the financial dashboard, PayPal Sandbox integration, AI Copilot, forecasting, and automated Postman API tests.

## Author

**Jyothi Srinivasan**

GitHub: https://github.com/JyothiSrinivasan

Project repository: https://github.com/JyothiSrinivasan/Clearflow

## License

MIT License — see [LICENSE](LICENSE).