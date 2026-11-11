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

```bash
streamlit run app.py
```

Open the local application at:

`http://127.0.0.1:8400`

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

## Hackathon Demo

**Demo video:** Add the public YouTube link here after recording.

## Author

**Jyothi Srinivasan**

GitHub: https://github.com/JyothiSrinivasan

## License

MIT License — see [LICENSE](LICENSE).