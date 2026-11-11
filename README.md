# Clearflow 2.0

**Your cash flow, clearly in view.**

### AI-Powered PayPal Payment Intelligence & Cash-Flow Forecasting

Clearflow 2.0 is a FinTech prototype developed for the **PayPal AI Hackathon 2026**. It combines PayPal Sandbox payment processing, verified payment synchronization, local AI-powered financial analysis, and interactive cash-flow forecasting in a unified dashboard.

The application features a Terracotta & Cream interface designed for clear, accessible financial insights.

## Key Features

### 1. Financial Dashboard
- Track synthetic INR income, expenses, and net cash flow.
- Add and review transactions.
- Store financial records in SQLite.

### 2. PayPal Sandbox Integration
- Create PayPal Sandbox checkout orders.
- Approve and capture test payments.
- Retrieve existing orders through PayPal APIs.
- Store verified payment information in SQLite.
- Track payment status, order ID, capture ID, amount, and currency.

### 3. AI Financial Copilot
- Uses a locally running Ollama language model (`qwen2.5:3b`).
- Analyzes synthetic financial data alongside synchronized PayPal Sandbox records.
- Answers questions about completed payments, captured amounts, expenses, and cash flow.
- Keeps USD Sandbox payments separate from INR ledger totals.

### 4. Cash-Flow Forecasting
- INR baseline projections using synthetic financial transactions.
- Separate USD scenario forecasts using user-defined assumptions.
- Adjustable opening balances, forecast periods, expected receipts, and expenses.
- Interactive Plotly visualizations.

**Forecasts are illustrative estimates, not guaranteed financial predictions.**

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Programming language | Python |
| Payment integration | PayPal Sandbox REST APIs |
| Database | SQLite |
| AI model | Ollama — Qwen2.5 3B |
| Charts | Plotly |
| Configuration | Python-dotenv |
| Version control | Git & GitHub |

## Architecture

```text
                 Clearflow 2.0
                       |
          Streamlit User Interface
                       |
       +---------------+---------------+
       |               |               |
   INR Ledger      PayPal API      AI Copilot
       |               |               |
       |          Verified Orders      |
       |               |               |
       +------------ SQLite -----------+
                       |
                Financial Context
                       |
                 Local Ollama
                       |
                AI Explanations

   Separate INR and USD Forecast Modules
                       |
                Plotly Charts
```

## Getting Started

### Prerequisites

- Python 3.13 or a compatible Python version
- Git
- Ollama installed locally
- PayPal Developer Sandbox credentials

### 1. Clone the repository

```bash
git clone https://github.com/JyothiSrinivasan/Clearflow.git
cd Clearflow
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure PayPal Sandbox

Copy `.env.example` to `.env` and provide your own PayPal Sandbox API credentials.

```env
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
```

Never commit `.env` or actual credentials.

### 5. Start Ollama

```bash
ollama pull qwen2.5:3b
```

Make sure Ollama is running before using the AI Copilot.

### 6. Run Clearflow

Make sure your Python virtual environment is activated, dependencies are installed, and Ollama is running with the `qwen2.5:3b` model available.

Start the application:

```powershell
python -m streamlit run app.py
```

Clearflow will be available at:

**http://127.0.0.1:8400**

The port and local address are configured in `.streamlit/config.toml`.

**Note:** To test PayPal payments, configure your own PayPal Sandbox credentials in `.env` using `.env.example` as a template.

## Demonstration Workflow

1. Open the financial dashboard.
2. Review or add synthetic INR transactions.
3. Create and capture a PayPal Sandbox payment.
4. Synchronize the verified PayPal order.
5. Ask the AI Copilot to explain the payment activity.
6. Explore the INR and USD cash-flow forecast charts.

## Important Limitations

- PayPal transactions use Sandbox test funds only.
- INR ledger records are synthetic demonstration data.
- PayPal synchronization retrieves known orders; it does not import complete account transaction history.
- USD Sandbox payments are not automatically converted or reconciled into INR totals.
- USD forecasts use manually entered assumptions, not a trained payment prediction model.
- The AI Copilot provides informational explanations, not regulated financial advice.
- Local PayPal credentials and Ollama setup are required to reproduce the complete workflow.

## PayPal Sandbox API Testing with Postman

Clearflow includes a Postman collection for testing its PayPal Sandbox API integration.

**Collection file:** `Clearflow_Postman_Collection.json`

The collection contains two requests:

| Request | Purpose |
|---|---|
| `01 - PayPal OAuth Access Token` | Authenticates with PayPal Sandbox using OAuth 2.0 |
| `02 - Retrieve PayPal Order` | Retrieves an existing Sandbox order and verifies its payment details |

### Automated API Test Results

Six automated checks passed during local testing:

| Test | Result |
|---|---|
| Order retrieval returns HTTP 200 | Passed |
| PayPal order is completed | Passed |
| Payment capture is completed | Passed |
| Payment amount and currency match $1.00 USD | Passed |
| Capture amount matches order amount | Passed |
| Gross payment minus PayPal fee equals net settlement | Passed |

**Test result: 6/6 passed.**

Example Sandbox transaction:

- Payment amount: $1.00 USD
- PayPal fee: $0.54 USD
- Net settlement: $0.46 USD
- Order status: COMPLETED
- Capture status: COMPLETED

These tests validate API responses and payment-data consistency. They do not represent a comprehensive security audit.

### Running the Postman Tests

1. Install Postman and import `Clearflow_Postman_Collection.json`.
2. Create your own PayPal Sandbox application through the PayPal Developer Dashboard.
3. Open Postman Local Vault and add:
   - `paypal_client_id`
   - `paypal_client_secret`
4. Use the corresponding PayPal Sandbox credentials as the Vault secret values.
5. If prompted, allow the trusted collection's scripts to access Vault secrets.
6. Run `01 - PayPal OAuth Access Token` to verify authentication.
7. Run `02 - Retrieve PayPal Order` to verify order retrieval and automated assertions.

The second request uses a pre-request script to obtain a temporary OAuth access token from PayPal Sandbox.

**Important:** The included order ID belongs to a demonstration Sandbox transaction. Judges using different Sandbox accounts may need to replace it with an order created under their own credentials. The example-specific assertions for the order ID, amount, and status may also need updating.

### Security Practices

- PayPal Client ID and Client Secret are loaded from local environment variables by the application.
- `.env` is excluded from Git tracking.
- `.env.example` contains placeholder configuration values.
- Postman Vault is used for API credentials.
- The exported collection uses Vault references instead of actual credentials.
- PayPal Sandbox is used instead of production payment processing.
- INR demonstration transactions and USD PayPal Sandbox payments are maintained separately.

### Application Setup Reminder

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install and run Ollama with the required model:

```powershell
ollama pull qwen2.5:3b
```

Ensure Ollama is running locally and configure `.env` using `.env.example`.

Launch Clearflow:

```powershell
python -m streamlit run app.py
```

Open:

`http://127.0.0.1:8400`

Clearflow runs locally by default. The GitHub repository provides the source code and setup instructions for judges to run the application themselves.

## Hackathon Demo

**Demo video:** Add the public YouTube link here after recording.

## Author

**Jyothi Srinivasan**

GitHub: https://github.com/JyothiSrinivasan

## License

MIT License — see [LICENSE](LICENSE).