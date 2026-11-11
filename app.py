from database import init_database, get_transactions, add_transaction
from forecast_service import generate_forecast
from ai_service import ask_clearflow
import streamlit as st
import requests

from paypal_service import create_order, get_order, capture_order

st.set_page_config(
    page_title="Clearflow | Financial Intelligence",
    page_icon="🌊",
    layout="wide"
)

init_database()
transactions = get_transactions()

income = sum(
    t["Amount"] for t in transactions
    if t["Type"] == "Income"
)
expenses = sum(
    t["Amount"] for t in transactions
    if t["Type"] == "Expense"
)

st.title("🌊 Clearflow")
st.caption("Your cash flow, clearly in view.")

st.info(
    "Sandbox demonstration: INR dashboard figures are synthetic. "
    "PayPal payments use test funds in USD."
)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "💳 PayPal Payments",
    "🤖 AI Copilot",
    "📈 Cash-Flow Forecast"
])

with tab1:
    st.subheader("Financial Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Income", f"₹{income:,.0f}")
    c2.metric("Total Expenses", f"₹{expenses:,.0f}")
    c3.metric(
        "Net Cash Flow",
        f"₹{income - expenses:,.0f}"
    )

    st.subheader("Transaction Activity")

    for t in transactions:
        symbol = "🟢" if t["Type"] == "Income" else "🔴"
        st.write(
            f'{symbol} {t["Date"]} | {t["Category"]} | '
            f'{t["Type"]} | ₹{t["Amount"]:,.0f}'
        )

    st.divider()
    st.subheader("➕ Add Transaction")

    with st.form("new_transaction_form"):
        date = st.date_input("Transaction date")
        transaction_type = st.selectbox(
            "Transaction type",
            ["Income", "Expense"]
        )
        category = st.text_input(
            "Category",
            placeholder="Sales, Rent, Supplies..."
        )
        transaction_amount = st.number_input(
            "Amount (INR)",
            min_value=1.0,
            value=1000.0,
            step=100.0
        )

        submitted = st.form_submit_button(
            "Save Transaction"
        )

        if submitted:
            try:
                add_transaction(
                    date,
                    transaction_type,
                    category,
                    transaction_amount
                )
                st.success("Transaction saved successfully!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))


with tab2:
    st.subheader("PayPal Sandbox Checkout")
    st.caption("All transactions are test payments.")

    amount = st.number_input(
        "Payment amount (USD)",
        min_value=1.00,
        max_value=1000.00,
        value=1.00,
        step=1.00
    )

    if "paypal_order_id" not in st.session_state:
        st.session_state.paypal_order_id = None

    if "paypal_approval_url" not in st.session_state:
        st.session_state.paypal_approval_url = None

    if st.button("Create PayPal Test Payment"):
        try:
            order_id, approval_url = create_order(amount)

            st.session_state.paypal_order_id = order_id
            st.session_state.paypal_approval_url = approval_url

            st.success("Sandbox order created successfully!")
        except (requests.RequestException, RuntimeError) as e:
            st.error(f"Unable to create order: {e}")

    if st.session_state.paypal_order_id:
        st.write(
            "**Order ID:**",
            st.session_state.paypal_order_id
        )

        if st.session_state.paypal_approval_url:
            st.link_button(
                "Approve Payment in PayPal Sandbox",
                st.session_state.paypal_approval_url
            )

        if st.button("Check Payment Status"):
            try:
                data = get_order(
                    st.session_state.paypal_order_id
                )
                st.write("**Order status:**", data["status"])
            except requests.RequestException as e:
                st.error(f"Unable to check status: {e}")

        if st.button("Capture Approved Payment"):
            try:
                data = get_order(
                    st.session_state.paypal_order_id
                )

                if data.get("status") == "APPROVED":
                    result = capture_order(
                        st.session_state.paypal_order_id
                    )

                    if result.get("status") == "COMPLETED":
                        st.success(
                            "PayPal Sandbox payment completed!"
                        )
                    else:
                        st.warning(
                            f"Order status: {result.get('status')}"
                        )
                elif data.get("status") == "COMPLETED":
                    st.info("This order is already completed.")
                else:
                    st.warning(
                        "Buyer approval is required first. "
                        f"Current status: {data.get('status')}"
                    )

            except requests.RequestException as e:
                st.error(f"Payment capture failed: {e}")


with tab3:
    st.subheader("🤖 Clearflow AI Financial Copilot")

    st.caption(
        "Powered by Ollama Qwen2.5:3b | "
        "Local AI | Synthetic financial data"
    )

    st.write(
        "Ask questions about your business income, "
        "expenses, cash flow, and financial decisions."
    )

    question = st.text_input(
        "Ask Clearflow",
        placeholder="Can my business afford a ₹20,000 expense?",
        key="ai_question"
    )

    if st.button("Ask Clearflow AI"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Clearflow AI is analysing..."):
                try:
                    answer = ask_clearflow(
                        question,
                        income,
                        expenses
                    )

                    st.markdown("### AI Financial Analysis")
                    st.write(answer)

                except requests.RequestException as e:
                    st.error(
                        "Could not connect to Ollama. "
                        "Check that Ollama is running."
                    )
                    st.caption(str(e))
                except (KeyError, ValueError) as e:
                    st.error(f"Unexpected AI response: {e}")


with tab4:
    st.subheader("📈 Cash-Flow Forecasting")

    st.caption(
        "Baseline forecast using synthetic transaction data. "
        "Future results are estimates, not guarantees."
    )

    days = st.selectbox(
        "Forecast horizon",
        [7, 14, 30]
    )

    opening_balance = st.number_input(
        "Assumed opening cash balance (INR)",
        min_value=0.0,
        value=0.0,
        step=1000.0
    )

    forecast = generate_forecast(
        transactions,
        days=days,
        opening_balance=opening_balance
    )

    if forecast:
        final_balance = forecast[-1]["Projected Balance"]

        c1, c2 = st.columns(2)

        c1.metric(
            "Projected Ending Balance",
            f"₹{final_balance:,.2f}"
        )

        c2.metric(
            "Forecast Period",
            f"{days} days"
        )

        st.subheader("Projected Cash Balance")

        # Native Streamlit chart; no direct Pandas import.
        try:
            st.line_chart(
                {
                    "Projected Balance": [
                        row["Projected Balance"]
                        for row in forecast
                    ]
                }
            )
        except Exception:
            st.warning(
                "Chart unavailable in this environment. "
                "Forecast calculations are still available."
            )

        st.subheader("Daily Forecast")

        for row in forecast:
            st.write(
                f'{row["Date"]}: '
                f'₹{row["Projected Balance"]:,.2f}'
            )


st.divider()
st.caption("Clearflow | PayPal AI Hackathon 2026")
