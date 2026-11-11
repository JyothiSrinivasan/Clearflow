from paypal_forecast import generate_paypal_forecast
import html
import requests
import streamlit as st

from database import (
    init_database, get_transactions, add_transaction,
    init_paypal_database, get_paypal_payments, save_paypal_payment,
)
from paypal_service import create_order, get_order, capture_order, normalize_paypal_order
from ai_service import ask_clearflow
from forecast_service import generate_forecast

st.set_page_config(page_title='Clearflow 2.0 | Payment Intelligence', page_icon='◈', layout='wide')
init_database()
init_paypal_database()
transactions = get_transactions()
payments = get_paypal_payments()
income = sum(t['Amount'] for t in transactions if t['Type'] == 'Income')
expenses = sum(t['Amount'] for t in transactions if t['Type'] == 'Expense')

st.markdown("""
<style>
/* Default text */
html, body, [data-testid="stApp"] {
    font-size: 19px !important;
}

/* Paragraphs and general text */
.stMarkdown p,
.stMarkdown li,
.stText,
.stAlert p {
    font-size: 19px !important;
    line-height: 1.7 !important;
}

/* Main title */
h1 {
    font-size: 36px !important;
    font-weight: 750 !important;
}

/* Section headings */
h2 {
    font-size: 26px !important;
}

h3 {
    font-size: 23px !important;
}

/* Sidebar navigation */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    font-size: 19px !important;
}

/* Buttons */
.stButton button,
.stFormSubmitButton button {
    font-size: 18px !important;
    min-height: 48px !important;
}

/* Input labels */
[data-testid="stWidgetLabel"] p {
    font-size: 18px !important;
}

/* Input fields */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    font-size: 19px !important;
}

/* KPI numbers */
[data-testid="stMetricValue"] {
    font-size: 32px !important;
}

/* KPI labels */
[data-testid="stMetricLabel"] p {
    font-size: 18px !important;
}

/* Captions */
[data-testid="stCaptionContainer"] p,
small {
    font-size: 16px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('''<style>
:root {color-scheme:light}
.stApp {background:#FFF8EF;color:#44352D}
[data-testid="stSidebar"] {background:#F0D9C8}
[data-testid="stHeader"] {background:#FFF8EF}
h1,h2,h3,h4,p,span,label {color:#44352D}
[data-testid="stMetric"] {background:#FFFFFF;border:1px solid #EBD9CB;
  border-radius:16px;padding:18px;box-shadow:0 3px 14px rgba(68,53,45,.05)}
[data-testid="stMetricLabel"] {color:#856F63}
[data-testid="stMetricValue"] {color:#44352D}
.stButton > button[kind="primary"],.stButton > button {
 background:#B95E43;color:white;border:0;border-radius:10px;font-weight:650;
 padding:.55rem 1.2rem}
.stButton > button:hover {background:#98472F;color:white;border:0}
[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {
 border-color:#EBD9CB;border-radius:16px}
[data-testid="stAlert"] {border-radius:12px}
.hero {background:linear-gradient(110deg,#B95E43,#D28B6A);border-radius:20px;
 padding:28px;color:#fff;margin-bottom:18px}
.hero h1,.hero p {color:white;margin:0}
.hero p {margin-top:8px;opacity:.95}
.pill {display:inline-block;background:#F0D9C8;color:#7A3E2C;
 padding:5px 12px;border-radius:30px;font-size:12px;font-weight:700}
.section-note {color:#856F63;font-size:14px}
</style>''', unsafe_allow_html=True)

st.markdown('''<div class="hero"><h1>◈ Clearflow 2.0</h1>
<p>Your cash flow, clearly in view. · AI-powered PayPal payment intelligence</p></div>''',
unsafe_allow_html=True)
st.info('Demo only: INR ledger data is synthetic. PayPal payments use USD sandbox test funds. Currencies are never silently combined.')

with st.sidebar:
    st.title('◈ Clearflow')
    st.caption('PAYMENT INTELLIGENCE')
    page = st.radio('Navigate', ['Overview', 'PayPal Intelligence', 'AI Copilot', 'Forecast', 'Transactions'])
    st.divider()
    st.caption('PayPal Sandbox · Local Ollama · SQLite')

if page == 'Overview':
    st.subheader('Financial overview')
    c1, c2, c3 = st.columns(3)
    c1.metric('Recorded income · INR', f'₹{income:,.0f}')
    c2.metric('Recorded expenses · INR', f'₹{expenses:,.0f}')
    c3.metric('Net cash flow · INR', f'₹{income-expenses:,.0f}')
    st.subheader('PayPal sandbox at a glance')
    completed = [p for p in payments if p['status'] == 'COMPLETED' and p.get('capture_id')]
    c1, c2, c3 = st.columns(3)
    c1.metric('Saved PayPal orders', len(payments))
    c2.metric('Completed captures', len(completed))
    c3.metric('Orders needing review', len(payments)-len(completed))
    st.caption('Sandbox payments are stored separately and excluded from INR totals.')
    st.subheader('Recent INR activity')
    if transactions:
        for t in reversed(transactions):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])

                col1.write(f"**{t['Category']}**")
                col1.caption(str(t["Date"]))

                col2.write(t["Type"])

                amount = float(t["Amount"])
                symbol = "+" if t["Type"] == "Income" else "-"

                col3.write(f"**{symbol}₹{amount:,.2f}**")
    else:
        st.info("No transactions available.")

elif page == 'PayPal Intelligence':
    st.subheader('PayPal sandbox checkout')
    st.caption('Create, approve, capture and save PayPal test orders. Sync a known order ID to retrieve its latest status.')
    amount = st.number_input('Payment amount (USD)', min_value=1.0, max_value=1000.0, value=1.0, step=1.0)
    if 'paypal_order_id' not in st.session_state:
        st.session_state.paypal_order_id = None
    if 'paypal_approval_url' not in st.session_state:
        st.session_state.paypal_approval_url = None
    if st.button('Create PayPal test payment'):
        try:
            order_id, approval_url = create_order(amount)
            st.session_state.paypal_order_id = order_id
            st.session_state.paypal_approval_url = approval_url
            save_paypal_payment(normalize_paypal_order(get_order(order_id)))
            st.success('Sandbox order created and saved.')
            st.rerun()
        except (requests.RequestException, RuntimeError, ValueError, KeyError) as exc:
            st.error(f'Could not create or save order: {exc}')
    order_id = st.session_state.paypal_order_id
    if order_id:
        st.code(order_id)
        if st.session_state.paypal_approval_url:
            st.link_button('Approve in PayPal Sandbox', st.session_state.paypal_approval_url)
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Check and save payment status'):
                try:
                    result = get_order(order_id)
                    save_paypal_payment(normalize_paypal_order(result))
                    st.success(f"PayPal order status: {result.get('status', 'UNKNOWN')}")
                    st.rerun()
                except (requests.RequestException, RuntimeError, ValueError, KeyError) as exc:
                    st.error(f'Unable to retrieve status: {exc}')
        with col2:
            if st.button('Capture approved payment'):
                try:
                    result = get_order(order_id)
                    if result.get('status') == 'APPROVED':
                        capture_order(order_id)
                        updated = get_order(order_id)
                        save_paypal_payment(normalize_paypal_order(updated))
                        st.success('Capture submitted; latest PayPal status saved.')
                        st.rerun()
                    elif result.get('status') == 'COMPLETED':
                        save_paypal_payment(normalize_paypal_order(result))
                        st.info('Order already completed and synced.')
                        st.rerun()
                    else:
                        st.warning(f"Buyer approval required. Current status: {result.get('status', 'UNKNOWN')}")
                except (requests.RequestException, RuntimeError, ValueError, KeyError) as exc:
                    st.error(f'Capture failed: {exc}')
    st.divider()
    st.subheader('Sync an existing sandbox order')
    with st.form('sync_order_form'):
        manual_order_id = st.text_input('PayPal Order ID', placeholder='Paste an order ID created with your sandbox credentials')
        sync = st.form_submit_button('Fetch and sync order')
        if sync:
            candidate = manual_order_id.strip()
            if not candidate or not candidate.isascii() or not candidate.isalnum() or len(candidate) > 64:
                st.error('Enter a valid PayPal order ID (letters and numbers only).')
            else:
                try:
                    save_paypal_payment(normalize_paypal_order(get_order(candidate)))
                    st.success('Verified PayPal order saved to SQLite.')
                    st.rerun()
                except (requests.RequestException, RuntimeError, ValueError, KeyError) as exc:
                    st.error(f'Sync failed: {exc}')
    st.subheader('Verified payment records')
    if payments:
        for payment in payments:
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**PayPal Order ID**")
                    st.write(payment["order_id"])

                    st.markdown("**Capture ID**")
                    st.write(payment.get("capture_id") or "Not captured")

                with col2:
                    st.markdown("**Payment status**")
                    st.write(payment["status"])

                    st.markdown("**Currency**")
                    st.write(payment["currency"])

                with col3:
                    st.markdown("**Amount**")
                    st.write(
                        f'{payment["currency"]} {payment["amount"]}'
                    )
    else:
        st.info('No PayPal orders saved yet. Create a test order or sync an existing order ID.')
    st.caption('Only orders retrieved from PayPal APIs are saved; this is not a full account-wide transaction import.')

elif page == 'AI Copilot':
    st.subheader('AI financial copilot')
    st.caption('Local Ollama · qwen2.5:3b · INR synthetic ledger + verified PayPal sandbox orders')
    st.markdown('<span class="pill">Payment-aware AI</span>', unsafe_allow_html=True)
    st.write('Ask about completed captures, pending orders, recorded expenses, or cash flow.')
    question = st.text_input('Ask Clearflow', placeholder='Which PayPal sandbox payments have been captured?')
    if st.button('Ask Clearflow AI'):
        if not question.strip():
            st.warning('Enter a question first.')
        else:
            with st.spinner('Analysing your saved records...'):
                try:
                    answer = ask_clearflow(question, income, expenses, payments)
                    st.markdown('#### Clearflow AI analysis')
                    st.write(answer)
                except (requests.RequestException, RuntimeError, KeyError, ValueError) as exc:
                    st.error('AI unavailable. Make sure Ollama is running with qwen2.5:3b.')
                    st.caption(str(exc))
    st.caption('The AI receives up to 30 recent saved PayPal orders; it cannot access unsynced PayPal history.')

elif page == 'Forecast':
    st.subheader('Cash-flow forecast')
    st.caption('Baseline projection from synthetic INR ledger. PayPal USD is excluded; no currency conversion is assumed.')
    days = st.selectbox('Forecast horizon', [7, 14, 30])
    opening_balance = st.number_input('Assumed opening cash balance (INR)', min_value=0.0, value=0.0, step=1000.0)
    forecast = generate_forecast(transactions, days=days, opening_balance=opening_balance)
    if forecast:
        st.metric('Projected ending balance · INR', f"₹{forecast[-1]['Projected Balance']:,.2f}")
        
        import plotly.graph_objects as go

        chart = go.Figure()

        chart.add_trace(
            go.Scatter(
                x=[r["Date"] for r in forecast],
                y=[r["Projected Balance"] for r in forecast],
                mode="lines+markers",
                line=dict(color="#B95E43", width=3),
                marker=dict(color="#E7B75D", size=8),
                hovertemplate="%{x}<br>₹%{y:,.2f}<extra></extra>",
                name="INR Forecast",
            )
        )

        chart.update_layout(
            title="Projected INR Cash Balance",
            paper_bgcolor="#FFF8EF",
            plot_bgcolor="#FFF8EF",
            font=dict(color="#44352D", size=16),
            xaxis_title="Date",
            yaxis_title="Balance (INR)",
            height=420,
            margin=dict(l=30, r=30, t=60, b=30),
        )

        chart.update_xaxes(showgrid=False)
        chart.update_yaxes(
            gridcolor="#EBD9CB",
            tickprefix="₹",
        )

        st.plotly_chart(
            chart,
            use_container_width=True,
            config={"displaylogo": False},
        )

        for row in forecast:
            st.write(
                f"{row['Date']} — ₹{row['Projected Balance']:,.2f}"
            )
    st.divider()
    st.subheader('PayPal payment exposure · USD')
    from decimal import Decimal, InvalidOperation
    usd = Decimal('0')
    for p in payments:
        if p['currency'] == 'USD' and p['status'] == 'COMPLETED' and p.get('capture_id'):
            try:
                usd += Decimal(p['amount'])
            except InvalidOperation:
                pass
    st.metric('Captured PayPal sandbox payments', f'${usd:,.2f}')
    st.caption('Separate observed sandbox total, not a future cash-flow prediction or converted INR balance.')


    st.divider()

    st.subheader("PayPal USD Cash-Flow Forecast")
    st.caption(
        "Scenario-based forecasting using saved PayPal Sandbox "
        "records and your assumptions. USD is kept separate "
        "from the synthetic INR ledger."
    )

    paypal_payments = get_paypal_payments()

    usd_col1, usd_col2 = st.columns(2)

    with usd_col1:
        paypal_days = st.selectbox(
            "PayPal forecast horizon",
            [7, 14, 30],
            key="paypal_forecast_days",
        )

        paypal_opening = st.number_input(
            "Assumed opening balance (USD)",
            min_value=0.0,
            value=100.0,
            step=10.0,
            key="paypal_opening",
        )

    with usd_col2:
        paypal_receipts = st.number_input(
            "Expected daily receipts (USD)",
            min_value=0.0,
            value=10.0,
            step=1.0,
            key="paypal_receipts",
        )

        paypal_expenses = st.number_input(
            "Expected daily expenses (USD)",
            min_value=0.0,
            value=4.0,
            step=1.0,
            key="paypal_expenses",
        )

    paypal_result = generate_paypal_forecast(
        payments=paypal_payments,
        days=paypal_days,
        opening_balance=paypal_opening,
        expected_daily_receipts=paypal_receipts,
        expected_daily_expenses=paypal_expenses,
    )

    st.markdown("### PayPal Payment Intelligence")

    p1, p2, p3 = st.columns(3)

    p1.metric(
        "Verified captured payments",
        paypal_result["completed_count"],
    )

    p2.metric(
        "Historical captured value",
        f'${paypal_result["historical_captured_usd"]:,.2f}',
    )

    p3.metric(
        "Projected ending balance",
        f'${paypal_result["projected_ending_balance_usd"]:,.2f}',
    )

    st.markdown("### Projected USD Balance")
    
    usd_chart = go.Figure()

    usd_chart.add_trace(
        go.Scatter(
            x=[r["Date"] for r in paypal_result["forecast"]],
            y=[
                r["Projected Balance"]
                for r in paypal_result["forecast"]
            ],
            mode="lines+markers",
            name="USD scenario",
            line=dict(color="#B95E43", width=3),
            marker=dict(size=7, color="#E7B75D"),
            hovertemplate=(
                "%{x}<br>$%{y:,.2f}<extra></extra>"
            ),
        )
    )

    usd_chart.update_layout(
        title="Projected PayPal USD Balance",
        paper_bgcolor="#FFF8EF",
        plot_bgcolor="#FFF8EF",
        font=dict(color="#44352D", size=16),
        xaxis_title="Date",
        yaxis_title="Balance (USD)",
        height=420,
        margin=dict(l=30, r=30, t=60, b=30),
    )

    usd_chart.update_xaxes(showgrid=False)
    usd_chart.update_yaxes(
        gridcolor="#EBD9CB",
        tickprefix="$",
    )

    st.plotly_chart(
        usd_chart,
        use_container_width=True,
        config={"displaylogo": False},
    )


    # Native text-based forecast avoids Pandas DLL errors.
    for item in paypal_result["forecast"]:
        with st.container(border=True):
            left, right = st.columns([2, 1])
            left.write(item["Date"])
            right.write(
                f'**${item["Projected Balance"]:,.2f}**'
            )

    st.info(
        "Historical PayPal Sandbox captures are shown as evidence "
        "of past payment activity. Future balances depend on the "
        "assumptions entered above and are not guaranteed."
    )

elif page == 'Transactions':
    st.subheader('INR transaction ledger')
    for t in reversed(transactions):
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            col1.write(str(t["Date"]))
            col2.write(f'{t["Category"]} ({t["Type"]})')
            col3.write(f'₹{t["Amount"]:,.2f}')
    st.subheader('Add transaction')
    with st.form('new_transaction_form'):
        date = st.date_input('Transaction date')
        transaction_type = st.selectbox('Transaction type', ['Income', 'Expense'])
        category = st.text_input('Category', placeholder='Sales, Rent, Supplies...')
        transaction_amount = st.number_input('Amount (INR)', min_value=1.0, value=1000.0, step=100.0)
        submitted = st.form_submit_button('Save transaction')
        if submitted:
            try:
                add_transaction(date, transaction_type, category, transaction_amount)
                st.success('Transaction saved successfully.')
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

st.divider()
st.caption('Clearflow 2.0 · PayPal AI Hackathon 2026 · Sandbox demonstration')
