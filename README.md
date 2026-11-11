# 🌊 Clearflow
### Your cash flow, clearly in view.

**AI-Powered Financial Intelligence for Small Businesses**

Built for the **PayPal AI Hackathon 2026**.

## Overview

Clearflow is a Python-based FinTech prototype that combines PayPal Sandbox payment processing, AI-powered financial explanations, persistent transaction tracking, and cash-flow forecasting in one Streamlit application.

The project demonstrates how small businesses can use payment APIs and locally running generative AI to better understand their financial activity.

## Key Features

### 1. Financial Dashboard
- Track business income and expenses.
- Add transactions through an interactive form.
- View total income, expenses, and net cash flow.
- Store transactions persistently using SQLite.

### 2. PayPal Sandbox Integration
- Create PayPal Sandbox payment orders.
- Open PayPal's buyer approval flow.
- Check payment status.
- Capture approved test payments.
- Authenticate securely using OAuth 2.0.

### 3. AI Financial Copilot
- Ask natural-language questions about business finances.
- Receive explanations grounded in calculated financial totals.
- Run the Qwen2.5:3b language model locally through Ollama.
- Avoid paid cloud-based LLM APIs.

### 4. Cash-Flow Forecasting
- Generate 7-, 14-, or 30-day baseline cash-flow projections.
- Configure an assumed opening balance.
- Review estimated daily cash balances.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Programming language | Python |
| Payment integration | PayPal REST API and Sandbox |
| AI | Ollama + Qwen2.5:3b |
| Database | SQLite |
| Forecasting | Python |
| API communication | Requests |
| Configuration | python-dotenv |

## Getting Started

### Prerequisites

- Python 3.13
- Git
- PayPal Developer Sandbox account
- Ollama installed locally

### Installation

Clone the repository:

```bash
git clone https://github.com/JyothiSrinivasan/Clearflow.git
cd Clearflow
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Configure PayPal Sandbox

Copy `.env.example` to a new file named `.env`.

Add your own PayPal Sandbox credentials:

```dotenv
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
```

Never commit `.env` or share your PayPal Client Secret.

### Configure Local AI

Install Ollama from https://ollama.com.

Download the model:

```bash
ollama pull qwen2.5:3b
```

Ensure Ollama is running before using the AI Copilot.

### Run Clearflow

```bash
python -m streamlit run app.py --server.port 8400
```

Open http://127.0.0.1:8400.

## How to Test

**Financial Dashboard:** Add an income or expense transaction and verify that the financial totals update.

**PayPal Payments:** Create a sandbox payment order, approve it using a PayPal Sandbox personal buyer account, check its status, and capture the approved payment.

**AI Copilot:** Ask, "What are my total expenses and net cash flow?"

**Forecasting:** Select a forecast horizon and review the projected balances.

## Architecture

```text
User
 |
 v
Streamlit Application
 |
 +-- SQLite Database
 |    +-- Transaction storage
 |    +-- Financial calculations
 |
 +-- PayPal Service
 |    +-- OAuth authentication
 |    +-- Sandbox Orders API
 |    +-- Payment capture
 |
 +-- AI Service
 |    +-- Ollama
 |    +-- Qwen2.5:3b
 |
 +-- Forecast Service
      +-- Baseline cash-flow projections
```

## Important Limitations

- This is a hackathon prototype, not a production financial service.
- Dashboard transactions are synthetic and denominated in INR.
- PayPal transactions use USD Sandbox test funds.
- PayPal payments are not automatically reconciled with the SQLite transaction ledger.
- Forecasts are baseline estimates, not validated machine-learning predictions.
- Ollama must be running locally for AI responses.
- Financial explanations are informational and should not be treated as professional financial advice.

## Demo Video

Public YouTube demonstration: **Coming soon**

## License

This project will be released under the MIT License.

## Author

**Jyothi Srinivasan**

GitHub: https://github.com/JyothiSrinivasan

Developed for the PayPal AI Hackathon 2026.