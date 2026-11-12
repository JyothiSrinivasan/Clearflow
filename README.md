# Clearflow

**Your cash flow, clearly in view.**

### AI-Powered PayPal Payment Intelligence & Cash-Flow Decision Support

Clearflow is an AI-assisted FinTech prototype developed for the **PayPal AI Hackathon 2026**.

It helps small businesses understand financial activity, verify PayPal Sandbox payments, explore future cash-flow scenarios, identify potential cash shortages, and make more informed financial decisions.

The application combines **PayPal Sandbox REST APIs, Python, SQLite, Streamlit, Plotly, and a locally hosted Ollama language model** in a unified financial dashboard.

Clearflow uses a modern **Midnight Navy & Mint/Teal** interface designed to make financial information accessible and easy to interpret.

## Key Features

### 1. Business Home

A financial overview dashboard featuring:

- Synthetic INR income, expenses, and net cash flow.
- Cash-flow activity visualization.
- Recent financial observations.
- Financial decision prompts.
- Quick access to other Clearflow modules.

### 2. Money Activity

Manage and review synthetic INR financial transactions.

- Add income and expense transactions.
- Store transactions locally in SQLite.
- Review recorded transaction activity.
- Remove eligible manually entered transactions.
- Analyze financial movements without mixing currencies.

### 3. Payment Centre — PayPal Sandbox

Clearflow integrates with PayPal Sandbox REST APIs to demonstrate payment processing and verification.

Features include:

- Create PayPal Sandbox checkout orders.
- Approve and capture test payments.
- Retrieve existing orders through PayPal APIs.
- Synchronize verified order information into SQLite.
- Review payment statuses, amounts, currencies, order IDs, and capture IDs.
- Keep PayPal USD payments separate from the synthetic INR ledger.

**Important:** Clearflow uses PayPal Sandbox only. No real-money payments are processed.

### 4. AI Financial Advisor

Clearflow uses the locally hosted **Ollama Qwen2.5 3B** language model to provide conversational financial assistance.

The advisor can:

- Answer questions about recorded financial activity.
- Explain income, expenses, and net cash flow.
- Discuss synchronized PayPal Sandbox payments.
- Summarize financial observations.
- Provide informational suggestions for small-business financial planning.

Python-calculated financial totals are supplied as verified context to reduce numerical errors.

**AI-generated explanations may still contain inaccuracies and should not be treated as verified financial calculations or professional financial advice.**

### 5. Cash-Flow Planner

Clearflow provides separate INR and USD planning experiences.

#### INR Cash-Flow Forecasting

- Baseline forecasts using synthetic INR financial activity.
- Interactive Plotly charts.
- Daily forecast details inside expandable sections.

#### Interactive INR Scenario Planner

Users can:

- Set an assumed opening cash balance.
- Set a minimum cash reserve.
- Choose a 7-, 14-, or 30-day planning horizon.
- Add expected income and expenses with dates and descriptions.
- View projected daily cash balances.
- Identify minimum-reserve breaches.
- Review deterministic cash-flow risk assessments.
- Request AI-assisted scenario explanations.

#### Interactive USD Scenario Planner

The USD planner provides an independent planning environment with:

- User-defined opening balance and minimum reserve.
- Expected USD income and expenses.
- Interactive cash-flow projections.
- Lowest projected balance and ending balance.
- Reserve-breach detection.
- Calculated cash shortfall amounts.
- Suggested actions for addressing potential cash shortages.
- AI-assisted explanations of scenario outcomes.

**INR and USD scenarios are calculated separately. Clearflow does not automatically convert or combine currencies.**

### 6. SQLite Scenario Save & Load

Both INR and USD planners support saving and restoring scenarios.

Users can:

- Assign a name to a scenario.
- Save planning assumptions and expected transactions.
- View previously saved scenarios.
- Load a saved scenario.
- Restore its opening balance, minimum reserve, planning horizon, and planned transactions.
- Continue modifying a loaded scenario.

Saved scenarios persist in the local SQLite database and can be restored after refreshing or restarting the application.

Unsaved scenario changes remain temporary.

Saved scenarios do not modify the recorded INR transaction ledger or create actual PayPal payments.

### 7. Cash-Flow Risk Detection

Clearflow uses deterministic Python calculations to identify potential cash-flow problems.

The system calculates:

- Projected ending balance.
- Lowest projected balance.
- Minimum cash reserve.
- Whether the reserve is breached.
- First reserve-breach date.
- Maximum shortfall relative to the reserve.

When a shortfall is detected, Clearflow displays a warning and practical options, such as collecting expected payments earlier, rescheduling expenses, or arranging sufficient short-term funds.

These are scenario-based decision-support suggestions, not guaranteed financial outcomes.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend and dashboard | Streamlit |
| Programming language | Python |
| Payment integration | PayPal Sandbox REST APIs |
| Database | SQLite |
| Local AI model | Ollama — Qwen2.5 3B |
| Financial calculations | Python, Decimal |
| Interactive charts | Plotly |
| API testing | Postman |
| Environment configuration | Python-dotenv |
| Version control | Git and GitHub |

## System Architecture

```text
                         CLEARFLOW
                             |
                    Streamlit Dashboard
                             |
          +------------------+------------------+
          |                  |                  |
     Business Home      Money Activity     Payment Centre
          |                  |                  |
     Financial KPIs      INR Ledger       PayPal Sandbox
          |                  |                  |
          +------------------+------------------+
                             |
                           SQLite
                             |
                  Recorded Financial Data
                             |
                    AI Financial Advisor
                             |
                    Local Ollama LLM

                    CASH-FLOW PLANNER
                             |
                +------------+------------+
                |                         |
          INR Scenario               USD Scenario
                |                         |
          Python Calculation Engine / Risk Detection
                |                         |
                +------------+------------+
                             |
                    Plotly Visualizations
                             |
                  SQLite Scenario Save/Load
                             |
                  AI Scenario Explanations
```

## Getting Started

### Prerequisites

- Python 3.13 or a compatible Python version.
- Git.
- Ollama installed locally.
- PayPal Developer Sandbox credentials.
- Postman (optional, for API testing).

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

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and enter your own PayPal Sandbox credentials:

```dotenv
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
```

Never commit `.env` or real credentials to GitHub.

### 5. Configure Ollama

Install the local model:

```bash
ollama pull qwen2.5:3b
```

Make sure Ollama is running.

Clearflow communicates with Ollama through:

`http://127.0.0.1:11434/api/chat`

### 6. Run Clearflow

```bash
python -m streamlit run app.py
```

Open:

**http://127.0.0.1:8400**

The local server address and port are configured in `.streamlit/config.toml`.

The AI features require Ollama. PayPal payment features require valid Sandbox credentials and an appropriate Sandbox account.

## Demonstration Workflow

1. Open **Business Home** and review the financial overview.
2. Navigate to **Money Activity** and inspect synthetic INR transactions.
3. Open **Payment Centre** to demonstrate PayPal Sandbox order creation, retrieval, capture, and verified payment records.
4. Use **AI Financial Advisor** to ask questions about financial activity.
5. Open **Cash-Flow Planner** and review the INR baseline forecast.
6. Create an INR scenario with expected income and expenses.
7. Review the projected cash-flow chart and reserve-risk assessment.
8. Save the INR scenario to SQLite and load it again.
9. Create a separate USD scenario and demonstrate a cash-reserve shortfall.
10. Save and load the USD scenario.
11. Generate an AI-assisted scenario explanation.
12. Review the Postman API verification tests.

## Example USD Cash-Flow Scenario

The following is an illustrative scenario using manually entered assumptions.

| Item | Amount |
|---|---:|
| Opening balance | $250 |
| Rent income | +$1,500 |
| Supplier payment | −$1,000 |
| Supplier payment | −$1,000 |
| Customer payment | +$2,000 |
| Customer payment | +$2,000 |
| Projected ending balance | **$3,750** |
| Lowest projected daily balance | **−$250** |
| Minimum reserve | **$200** |
| Maximum reserve shortfall | **$450** |

This example demonstrates how a business can experience a temporary cash shortage even when its projected ending balance is positive.

The example assumes the opening balance is measured before the first day's transactions and uses daily closing balances. All listed transactions must fall within the selected planning horizon.

These are hypothetical cash movements, not actual PayPal account balances or guaranteed future receipts.

## PayPal Sandbox API Testing with Postman

Clearflow includes a Postman collection for reproducing API authentication and payment-verification tests.

**Collection:** `Clearflow_Postman_Collection.json`

### Included API Requests

| Request | Purpose |
|---|---|
| `01 - PayPal OAuth Access Token` | Authenticate using PayPal Sandbox OAuth 2.0 |
| `02 - Retrieve PayPal Order` | Retrieve an existing Sandbox order and validate payment information |

### Automated Test Results

Six automated order-verification tests passed during local testing.

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
5. Add `paypal_client_id` and `paypal_client_secret` using your own Sandbox credentials.
6. Enable Vault access for trusted collection scripts when prompted.
7. Run `01 - PayPal OAuth Access Token`.
8. Run `02 - Retrieve PayPal Order`.
9. Review the automated assertions in the **Test Results** tab.

The second request obtains a temporary OAuth access token through its pre-request script.

**Note for judges:** The included order ID refers to a demonstration Sandbox payment. If using a different Sandbox merchant account, replace the order ID with one created under your own account. The automated assertions expect a completed $1.00 USD payment with a completed capture; use a matching test order or adjust the assertions accordingly.

These tests validate API behavior and payment-data consistency. They do not constitute a comprehensive application security assessment.

## Security Practices

- PayPal credentials are loaded from environment variables.
- `.env` is excluded from Git tracking.
- `.env.example` contains placeholder values.
- Postman Local Vault is used for API-testing credentials.
- The exported Postman collection references Vault secrets.
- PayPal Sandbox is used instead of live payment processing.
- Synthetic INR records and USD Sandbox payments are kept separate.
- Access tokens are obtained at runtime for authenticated requests.
- Scenario calculations are performed using Python rather than relying on the language model for arithmetic.
- Local SQLite data is not intended to be committed to the public repository.

## Important Limitations

- PayPal transactions use Sandbox test funds only.
- INR ledger records are synthetic demonstration data.
- PayPal synchronization retrieves known orders rather than automatically importing complete account history.
- INR and USD financial values are not silently combined or converted.
- Scenario forecasts are based on manually entered assumptions.
- Forecasts are illustrative and are not guaranteed predictions.
- The AI model may generate inaccurate explanations, including incorrect dates or financial interpretations.
- Python-calculated scenario metrics and risk assessments should be treated as authoritative within the stated assumptions.
- The application does not provide regulated financial advice.
- The complete workflow requires local setup.
- Saved scenarios persist in a local SQLite database, not in a cloud account.
- Clearflow runs locally by default and is not a publicly hosted service.
- The prototype does not provide production-grade authentication, multi-user isolation, or financial-data security controls.

## 🎥 Clearflow Hackathon Demo

Watch the working demonstration of Clearflow, developed for
the PayPal AI Hackathon 2026.

[![Watch Clearflow Hackathon Demo](https://img.youtube.com/vi/TnzLOMaOFPA/maxresdefault.jpg)](https://youtu.be/TnzLOMaOFPA)

▶️ **[Watch the Full Demo on YouTube](https://youtu.be/TnzLOMaOFPA)**

### What's demonstrated?

- Financial dashboard and transaction management
- PayPal Sandbox payment integration
- AI Financial Advisor powered by Ollama
- INR and USD cash-flow planning
- Cash-reserve shortfall detection
- SQLite scenario saving and loading
- PayPal API verification using Postman
## Author

**Jyothi Srinivasan**

GitHub: https://github.com/JyothiSrinivasan

Project repository: https://github.com/JyothiSrinivasan/Clearflow

## License

MIT License — see [LICENSE](LICENSE).