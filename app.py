from paypal_forecast import generate_paypal_forecast
import html
import requests
import streamlit as st
from scenario_planner import calculate_scenario
import plotly.graph_objects as go
from datetime import date, timedelta
from database import save_scenario, list_saved_scenarios, load_scenario
from database import (
    init_database, get_transactions, add_transaction,
    delete_transaction,
    init_paypal_database, get_paypal_payments, save_paypal_payment,
)

from paypal_service import create_order, get_order, capture_order, normalize_paypal_order
from ai_service import ask_clearflow
from forecast_service import generate_forecast

def restore_saved_scenario(scenario_id, currency):
    saved = load_scenario(scenario_id)

    if saved is None:
        return

    if saved["currency"] != currency:
        raise ValueError("Saved scenario currency mismatch.")

    if currency == "INR":
        prefix = "scenario"
        events_key = "planned_cash_events"
    else:
        prefix = "usd_scenario"
        events_key = "usd_planned_events"

    st.session_state[f"{prefix}_opening"] = float(
        saved["opening_balance"]
    )

    st.session_state[f"{prefix}_reserve"] = float(
        saved["minimum_reserve"]
    )

    st.session_state[f"{prefix}_days"] = int(
        saved["planning_days"]
    )

    st.session_state[events_key] = [
        {
            "date": event["date"],
            "type": event["type"],
            "category": event["description"],
            "amount": float(event["amount"]),
        }
        for event in saved["events"]
    ]

st.set_page_config(page_title='Clearflow | Payment Intelligence', page_icon='◈', layout='wide')
init_database()
init_paypal_database()
transactions = get_transactions()
payments = get_paypal_payments()
income = sum(t['Amount'] for t in transactions if t['Type'] == 'Income')
expenses = sum(t['Amount'] for t in transactions if t['Type'] == 'Expense')


st.markdown("""
<style>
/* CLEARFLOW — MIDNIGHT FINANCE */

/* Main workspace */
.stApp {
    background: #0B1424;
    color: #E8F0FA;
}

[data-testid="stHeader"] {
    background: #0B1424;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #101E30;
    border-right: 1px solid #293B50;
}

[data-testid="stSidebar"] * {
    color: #DCE8F4;
}

/* Navigation */
[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 10px;
    padding: 8px 10px;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #1D3448;
}

/* Headings */
h1, h2, h3, h4 {
    color: #F1F7FD;
    font-weight: 700;
}

.stMarkdown p,
.stMarkdown li {
    line-height: 1.65;
}

/* Financial metric cards */
[data-testid="stMetric"] {
    background: #17263A;
    border: 1px solid #2A4056;
    border-radius: 16px;
    padding: 20px;
}

[data-testid="stMetricLabel"] p {
    color: #A6B9CD;
    font-size: 15px;
}

[data-testid="stMetricValue"] {
    color: #4ADEAE;
    font-size: 32px;
    font-weight: 750;
}

/* Containers and forms */
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stForm"] {
    border-color: #2A4056;
    border-radius: 16px;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background: #4ADEAE;
    color: #09251E;
    border: 1px solid #4ADEAE;
    border-radius: 10px;
    font-weight: 700;
    min-height: 44px;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #78EAC2;
    color: #09251E;
    border-color: #78EAC2;
}

/* Text inputs */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background: #17263A;
    color: #F1F7FD;
    border: 1px solid #354C63;
    border-radius: 10px;
}

/* Hero */
.hero {
    background: linear-gradient(110deg, #13273B, #174D4A);
    border: 1px solid #2B625B;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 20px;
}

.hero h1 {
    color: #FFFFFF;
    margin: 0;
    font-size: 34px;
}

.hero p {
    color: #BDD7D5;
    margin-top: 10px;
    margin-bottom: 0;
}

/* AI label */
.pill {
    display: inline-block;
    background: #183E3B;
    color: #4ADEAE;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
}

/* Dividers */
hr {
    border-color: #2A4056;
}

/* Captions */
[data-testid="stCaptionContainer"] p {
    color: #A6B9CD;
}

/* Links */
a {
    color: #4ADEAE;
}


/* Clearflow sidebar improvements */
[data-testid="stSidebar"] {
    min-width: 280px !important;
    max-width: 280px !important;
}

[data-testid="stSidebar"] h1 {
    font-size: 29px !important;
    font-weight: 800 !important;
}

[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    font-size: 16px !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 12px 14px !important;
    margin-bottom: 7px;
    border-radius: 12px;
    transition: background 0.2s ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label p {
    font-size: 18px !important;
    font-weight: 600 !important;
    line-height: 1.4 !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #1C3449;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    font-size: 13px !important;
    line-height: 1.5 !important;
}


/* Compact workspace header */
.workspace-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    background: #132337;
    border: 1px solid #2A4056;
    border-radius: 14px;
    padding: 16px 22px;
    margin-bottom: 16px;
}

.workspace-eyebrow {
    color: #E8F0FA;
    font-size: 16px;
    font-weight: 750;
    letter-spacing: 0.5px;
}

.workspace-description {
    color: #A6B9CD;
    font-size: 14px;
    margin-top: 5px;
}

.workspace-status {
    background: #173D37;
    color: #4ADEAE;
    border: 1px solid #2B6657;
    border-radius: 30px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 700;
    white-space: nowrap;
}

@media (max-width: 700px) {
    .workspace-header {
        flex-direction: column;
        align-items: flex-start;
    }
}


/* CLEARFLOW — READABILITY & TOP NAVIGATION */

/* Hide the unused sidebar */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* Make better use of desktop width */
.block-container {
    max-width: 1550px !important;
    padding-top: 2rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
}

/* Larger headings */
h1 { font-size: 38px !important; }
h2 { font-size: 30px !important; }
h3 { font-size: 25px !important; }
h4 { font-size: 21px !important; }

/* Larger normal text */
.stMarkdown p,
.stMarkdown li,
.stText,
[data-testid="stWidgetLabel"] p {
    font-size: 18px !important;
    line-height: 1.65 !important;
}

/* More readable descriptions */
[data-testid="stCaptionContainer"] p,
small {
    font-size: 15px !important;
    line-height: 1.55 !important;
}

/* Bigger financial figures */
[data-testid="stMetricValue"] {
    font-size: 38px !important;
    font-weight: 800 !important;
}

/* Metric labels */
[data-testid="stMetricLabel"] p {
    font-size: 17px !important;
}

/* Larger buttons and forms */
.stButton button,
.stFormSubmitButton button {
    font-size: 17px !important;
    min-height: 46px !important;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox,
.stDateInput {
    font-size: 17px !important;
}

/* Navigation title */
.nav-section-label {
    color: #A6B9CD;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin: 18px 0 10px;
}

/* Horizontal navigation */
div[data-testid="stRadio"] [role="radiogroup"] {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 10px;
    background: #17263A;
    border: 1px solid #2A4056;
    border-radius: 14px;
}

div[data-testid="stRadio"] [role="radiogroup"] label {
    background: #203247;
    border-radius: 10px;
    padding: 10px 14px;
    margin: 0;
}

div[data-testid="stRadio"] [role="radiogroup"] label p {
    font-size: 17px !important;
    font-weight: 650 !important;
    white-space: nowrap;
}

/* Keep mobile layouts usable */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    h1 { font-size: 30px !important; }
    h2 { font-size: 26px !important; }

    div[data-testid="stRadio"] [role="radiogroup"] label p {
        font-size: 15px !important;
    }
}

</style>
""", unsafe_allow_html=True)



st.markdown("""
<div class="workspace-header">
    <div>
        <div class="workspace-eyebrow">
            CLEARFLOW / FINANCIAL INTELLIGENCE
        </div>
        <div class="workspace-description">
            Understand your money · Verify payments · Plan ahead
        </div>
    </div>
    <span class="workspace-status">
        ● SANDBOX DEMO
    </span>
</div>
""", unsafe_allow_html=True)


st.info('Demo only: INR ledger data is synthetic. PayPal payments use USD sandbox test funds. Currencies are never silently combined.')


# Clearflow top navigation
st.markdown(
    '<div class="nav-section-label">YOUR FINANCIAL WORKSPACE</div>',
    unsafe_allow_html=True
)

page = st.radio(
    "Navigate",
    [
        "Business Home",
        "Money Activity",
        "Payment Centre",
        "AI Financial Advisor",
        "Cash-Flow Planner"
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="clearflow_navigation"
)



if page == 'Business Home':
    import plotly.graph_objects as go
    from collections import defaultdict

    st.title("Business Home")
    st.caption(
        "Your financial command centre — understand activity, "
        "review payments, and plan your next decision."
    )

    net_cash = income - expenses
    expense_ratio = (
        expenses / income * 100 if income > 0 else None
    )

    # Main financial position
    st.subheader("Your financial position")
    k1, k2, k3 = st.columns(3)

    k1.metric("Net cash flow · INR", f"₹{net_cash:,.0f}")
    k2.metric("Recorded income · INR", f"₹{income:,.0f}")
    k3.metric("Recorded expenses · INR", f"₹{expenses:,.0f}")

    st.caption(
        "Synthetic INR ledger totals. Net cash flow is income "
        "minus expenses, not a verified bank account balance."
    )

    st.divider()

    # Actual cumulative transaction movement
    left, right = st.columns([1.6, 1], gap="large")

    with left:
        st.subheader("Cash-flow activity")

        daily_changes = defaultdict(float)

        for t in transactions:
            amount = float(t["Amount"])
            signed = (
                amount if t["Type"] == "Income" else -amount
            )
            daily_changes[str(t["Date"])] += signed

        if daily_changes:
            dates = sorted(daily_changes)
            balances = []
            running_total = 0.0

            for day in dates:
                running_total += daily_changes[day]
                balances.append(running_total)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=balances,
                mode="lines+markers",
                name="Cumulative net flow",
                line=dict(color="#4ADEAE", width=3),
                marker=dict(size=8, color="#4ADEAE"),
                fill="tozeroy",
                fillcolor="rgba(74,222,174,0.10)",
                hovertemplate=(
                    "%{x}<br>₹%{y:,.2f}<extra></extra>"
                )
            ))

            fig.update_layout(
                paper_bgcolor="#17263A",
                plot_bgcolor="#17263A",
                font=dict(
                    color="#E8F0FA",
                    size=17
                ),
                xaxis_title="Transaction date",
                yaxis_title="Cumulative net flow (INR)",
                height=350,
                margin=dict(l=15, r=15, t=20, b=20),
                showlegend=False,
                xaxis=dict(
                    title_font=dict(size=17),
                    tickfont=dict(size=15)
                ),
                yaxis=dict(
                    title_font=dict(size=17),
                    tickfont=dict(size=15)
                ),
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(
                gridcolor="#304258",
                tickprefix="₹"
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displaylogo": False}
            )
            st.caption(
                "Cumulative net transaction flow, starting "
                "from zero. Not a bank balance or forecast."
            )
        else:
            st.info("Add transactions to see cash-flow activity.")

    with right:
        st.subheader("Financial observations")

        if expense_ratio is not None:
            st.metric(
                "Expenses as % of income",
                f"{expense_ratio:.1f}%"
            )
            st.write(
                f"₹{expenses:,.0f} of recorded expenses "
                f"against ₹{income:,.0f} of income."
            )
        else:
            st.info(
                "An expense-to-income ratio is unavailable "
                "until income is recorded."
            )

        expense_categories = defaultdict(float)

        for t in transactions:
            if t["Type"] == "Expense":
                expense_categories[t["Category"]] += float(
                    t["Amount"]
                )

        if expense_categories:
            category, amount = max(
                expense_categories.items(),
                key=lambda item: item[1]
            )
            st.write("**Largest recorded expense category**")
            st.write(f"{category}: ₹{amount:,.0f}")

        st.caption(
            "These observations are calculated from the "
            "ledger, not generated by AI."
        )

    st.divider()

    # Payment health
    st.subheader("Digital payment activity")

    completed = [
        p for p in payments
        if p["status"] == "COMPLETED"
        and p.get("capture_id")
    ]

    p1, p2, p3 = st.columns(3)
    p1.metric("Saved sandbox orders", len(payments))
    p2.metric("Completed captures", len(completed))
    p3.metric(
        "Orders needing review",
        len(payments) - len(completed)
    )

    st.caption(
        "PayPal Sandbox payments are in their original "
        "currencies and excluded from INR ledger totals."
    )

    st.divider()

    # Decision-making prompts
    
    st.subheader("Make smarter financial decisions")

    action1, action2 = st.columns(2, gap="large")

    with action1:
        with st.container(border=True):
            st.markdown("### Get AI-powered financial insights")
            st.write(
                "Ask Clearflow AI about your recorded income, "
                "expenses, payment activity, and cash-flow decisions."
            )
            st.caption("Explore AI Financial Advisor")

    with action2:
        with st.container(border=True):
            st.markdown("### Plan your financial future")
            st.write(
                "Explore 7-, 14-, and 30-day cash-flow projections "
                "and assess how financial assumptions affect your plans."
            )
            st.caption("Explore Cash-Flow Planner")

    st.divider()

    st.subheader("Latest INR transactions")

    if transactions:
        for t in transactions[:5]:
            with st.container(border=True):
                a, b, c = st.columns([2, 2, 1])

                a.write(f"**{t['Category']}**")
                a.caption(str(t["Date"]))

                b.write(t["Type"])

                sign = (
                    "+" if t["Type"] == "Income" else "-"
                )
                c.write(
                    f"**{sign}₹{float(t['Amount']):,.2f}**"
                )
    else:
        st.info("No INR transactions recorded.")

elif page == 'Payment Centre':
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

elif page == 'AI Financial Advisor':
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

elif page == 'Cash-Flow Planner':
    st.title('Cash-Flow Planner')
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
                line=dict(color="#4ADEAE", width=4),
                marker=dict(color="#4ADEAE", size=9),
                hovertemplate="%{x}<br>₹%{y:,.2f}<extra></extra>",
                name="INR Forecast",
            )
        )

        
        chart.update_layout(
            title=dict(
                text="Projected INR Cash Balance",
                font=dict(size=23, color="#F1F7FD")
            ),
            paper_bgcolor="#17263A",
            plot_bgcolor="#17263A",
            font=dict(
                family="Arial",
                size=17,
                color="#E8F0FA"
            ),
            xaxis=dict(
                title="Forecast date",
                title_font=dict(size=18),
                tickfont=dict(size=15),
                showgrid=False,
                linecolor="#40546A"
            ),
            yaxis=dict(
                title="Projected balance (INR)",
                title_font=dict(size=18),
                tickfont=dict(size=15),
                gridcolor="#304258",
                tickprefix="₹",
                zerolinecolor="#40546A"
            ),
            height=440,
            margin=dict(l=30, r=30, t=75, b=35),
            showlegend=False,
            hovermode="x unified"
        )


        st.plotly_chart(
            chart,
            use_container_width=True,
            config={"displaylogo": False},
        )

        with st.expander(
            "View Daily INR Forecast Details",
            expanded=False,
        ):
            for row in forecast:
                st.write(
                    f"{row['Date']} — "
                    f"₹{row['Projected Balance']:,.2f}"
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

    
    # INTERACTIVE INR SCENARIO PLANNER
    st.divider()
    st.header("Interactive Business Scenario Planner")
    st.caption(
        "Test expected future payments and expenses. "
        "These scenarios do not change your recorded ledger."
    )

    from datetime import date, timedelta
    import plotly.graph_objects as go

    if "planned_cash_events" not in st.session_state:
        st.session_state.planned_cash_events = []

    with st.container(border=True):
        st.subheader("1. Set your planning assumptions")

        a, b, c = st.columns(3)

        with a:
            scenario_opening = st.number_input(
                "Assumed opening cash balance (INR)",
                min_value=0.0,
                value=20000.0,
                step=1000.0,
                key="scenario_opening",
            )

        with b:
            scenario_reserve = st.number_input(
                "Minimum cash reserve (INR)",
                min_value=0.0,
                value=10000.0,
                step=1000.0,
                key="scenario_reserve",
            )

        with c:
            scenario_days = st.selectbox(
                "Planning horizon",
                [7, 14, 30],
                key="scenario_days",
            )

    with st.container(border=True):
        st.subheader("2. Add expected cash movements")

        with st.form("planned_event_form", clear_on_submit=True):
            e1, e2 = st.columns(2)

            with e1:
                event_type = st.selectbox(
                    "Transaction type",
                    ["Income", "Expense"],
                )
                event_amount = st.number_input(
                    "Expected amount (INR)",
                    min_value=1.0,
                    value=1000.0,
                    step=100.0,
                )

            with e2:
                event_category = st.text_input(
                    "Description",
                    placeholder="Customer payment, rent, supplies...",
                )
                event_date = st.date_input(
                    "Expected transaction date",
                    value=date.today() + timedelta(days=1),
                    min_value=date.today() + timedelta(days=1),
                )

            add_event = st.form_submit_button(
                "Add planned transaction"
            )

        if add_event:
            if not event_category.strip():
                st.error("Please enter a description.")
            else:
                st.session_state.planned_cash_events.append({
                    "date": event_date.isoformat(),
                    "type": event_type,
                    "category": event_category.strip(),
                    "amount": float(event_amount),
                })
                st.rerun()

        if st.session_state.planned_cash_events:
            with st.expander(
                f"View planned transactions "
                f"({len(st.session_state.planned_cash_events)})",
                expanded=False,
            ):

                for index, event in enumerate(
                    st.session_state.planned_cash_events
                ):
                    c1, c2 = st.columns([5, 1])

                with c1:
                    st.write(
                        f"{event['date']} · {event['category']} · "
                        f"{event['type']} · ₹{event['amount']:,.2f}"
                    )

                with c2:
                    if st.button(
                        "Remove",
                        key=f"remove_planned_{index}",
                    ):
                        st.session_state.planned_cash_events.pop(index)
                        st.rerun()

            if st.button("Clear all planned transactions"):
                st.session_state.planned_cash_events = []
                st.rerun()
        else:
            st.info(
                "Add an expected income or expense to begin planning."
            )

        # SAVE / LOAD INR SCENARIOS
    with st.container(border=True):
        st.subheader("Save or load an INR scenario")

        inr_scenario_name = st.text_input(
            "Scenario name",
            placeholder="November Cash Flow Plan",
            key="inr_save_name",
        )

        if st.button("Save INR Scenario", key="save_inr"):
            try:
                scenario_id = save_scenario(
                    name=inr_scenario_name,
                    currency="INR",
                    opening_balance=scenario_opening,
                    minimum_reserve=scenario_reserve,
                    planning_days=scenario_days,
                    events=[
                        {
                            "date": event["date"],
                            "type": event["type"],
                            "description": event["category"],
                            "amount": event["amount"],
                        }
                        for event in st.session_state.planned_cash_events
                    ],
                )
                st.success(
                    f"INR scenario saved successfully! ID: {scenario_id}"
                )
            except (ValueError, KeyError) as exc:
                st.error(f"Could not save scenario: {exc}")

        saved_inr = list_saved_scenarios("INR")

        if saved_inr:
            scenario_options = {
                f"{item['name']} (ID {item['id']})": item["id"]
                for item in saved_inr
            }

            selected_inr = st.selectbox(
                "Select a saved INR scenario",
                options=list(scenario_options.keys()),
                key="selected_inr_scenario",
            )

            st.button(
                "Load INR Scenario",
                key="load_inr",
                on_click=restore_saved_scenario,
                args=(scenario_options[selected_inr], "INR"),
            )
        else:
            st.caption("No saved INR scenarios yet.")

    scenario = calculate_scenario(
        opening_balance=scenario_opening,
        minimum_reserve=scenario_reserve,
        horizon_days=scenario_days,
        planned_events=st.session_state.planned_cash_events,
    )

    st.subheader("3. Your projected cash position")

    s1, s2, s3 = st.columns(3)

    s1.metric(
        "Projected ending balance",
        f"₹{scenario['ending_balance']:,.2f}",
    )
    s2.metric(
        "Lowest projected balance",
        f"₹{scenario['lowest_balance']:,.2f}",
    )
    s3.metric(
        "Minimum reserve",
        f"₹{scenario['minimum_reserve']:,.2f}",
    )

    scenario_chart = go.Figure()

    scenario_chart.add_trace(
        go.Scatter(
            x=[r["Date"] for r in scenario["forecast"]],
            y=[
                r["Projected Balance"]
                for r in scenario["forecast"]
            ],
            mode="lines+markers",
            line=dict(color="#4ADEAE", width=4),
            marker=dict(color="#4ADEAE", size=8),
            fill="tozeroy",
            fillcolor="rgba(74,222,174,0.08)",
            name="Projected cash balance",
            hovertemplate="%{x}<br>₹%{y:,.2f}<extra></extra>",
        )
    )

    scenario_chart.add_hline(
        y=scenario_reserve,
        line_dash="dash",
        line_color="#F5B95C",
        annotation_text="Minimum reserve",
        annotation_font_color="#F5B95C",
    )

    scenario_chart.update_layout(
        title="Daily Cash-Flow Scenario · INR",
        paper_bgcolor="#17263A",
        plot_bgcolor="#17263A",
        font=dict(color="#E8F0FA", size=17),
        xaxis=dict(
            title="Date",
            showgrid=False,
            tickfont=dict(size=15),
        ),
        yaxis=dict(
            title="Projected cash balance (INR)",
            gridcolor="#304258",
            tickprefix="₹",
            tickfont=dict(size=15),
        ),
        height=460,
        margin=dict(l=35, r=35, t=75, b=40),
        showlegend=False,
        hovermode="x unified",
    )

    st.plotly_chart(
        scenario_chart,
        use_container_width=True,
        config={"displaylogo": False},
    )

    st.subheader("4. Cash-flow risk assessment")

    if scenario["reserve_breached"]:
        st.warning(
            "Cash reserve warning: the projected balance "
            f"falls below ₹{scenario_reserve:,.2f} "
            f"on {scenario['first_shortfall']}. "
            "Review payment timing or available funds."
        )
    else:
        st.success(
            "The projected cash balance stays at or above "
            "your minimum reserve under these assumptions."
        )

    st.caption(
        "Scenario results are deterministic calculations, "
        "not guaranteed outcomes or verified bank balances. "
        "Unsaved changes are temporary. Scenarios explicitly "
        "saved using Save Scenario are stored locally in SQLite."
    )

    
    st.subheader("5. AI-assisted financial explanation")

    if st.button(
        "Explain this scenario with Clearflow AI",
        key="explain_cash_scenario",
    ):
        import requests
        import json

        verified_facts = {
            "currency": "INR",
            "opening_balance": scenario["opening_balance"],
            "ending_balance": scenario["ending_balance"],
            "lowest_balance": scenario["lowest_balance"],
            "minimum_reserve": scenario["minimum_reserve"],
            "first_shortfall": scenario["first_shortfall"],
            "reserve_breached": scenario["reserve_breached"],
            "planned_events": st.session_state.planned_cash_events,
        }

        reserve_status = (
            "BREACHED"
            if scenario["reserve_breached"]
            else "NOT BREACHED"
        )

        reserve_gap = max(
            0.0,
            scenario["minimum_reserve"] - scenario["lowest_balance"],
        )

        system_message = (
            "You are Clearflow's financial scenario explainer. "
            "Python has already calculated all financial results. "
            "You must treat these results as authoritative. "
            f"Currency: INR. Reserve status: {reserve_status}. "
            f"Minimum reserve: {scenario['minimum_reserve']:.2f}. "
            f"Lowest balance: {scenario['lowest_balance']:.2f}. "
            f"Reserve shortfall: {reserve_gap:.2f}. "
            "If reserve status is NOT BREACHED, explicitly state "
            "that the minimum reserve is maintained throughout "
            "the planning horizon. Never claim a reserve breach "
            "or cash shortfall in that case. "
            "If reserve status is BREACHED, explain the shortfall "
            "and suggest practical steps to address it. "
            "Do not invent amounts, dates, or transactions. "
            "Do not recalculate the verified figures. "
            "Keep the explanation concise and practical. "
            "Do not guarantee future financial outcomes."
        )

        try:
            with st.spinner("Analysing your scenario..."):
                response = requests.post(
                    "http://127.0.0.1:11434/api/chat",
                    json={
                        "model": "qwen2.5:3b",
                        "stream": False,
                        "messages": [
                            {
                                "role": "system",
                                "content": system_message,
                            },
                            {
                                "role": "user",
                                "content": json.dumps(
                                    verified_facts
                                ),
                            },
                        ],
                    },
                    timeout=120,
                )
                response.raise_for_status()

                explanation = response.json()[
                    "message"
                ]["content"]

                # Validate AI explanation against verified reserve status.
                # This is a conservative keyword check, not full semantic validation.
                import re

                if not scenario["reserve_breached"]:
                    suspicious_claims = [
                        r"\bthere is a reserve breach\b",
                        r"\breserve (?:has been |was |is )?breached\b",
                        r"\bbelow (?:the )?minimum reserve\b",
                        r"\bshortfall of\b",
                        r"\bfinancial shortfall\b",
                    ]

                    if any(
                        re.search(pattern, explanation, re.IGNORECASE)
                        for pattern in suspicious_claims
                    ):
                        explanation = (
                            "The AI-generated interpretation was withheld "
                            "because it may contradict the verified "
                            "scenario calculations.\n\n"
                            f"Verified result: the lowest projected "
                            f"balance is ₹{scenario['lowest_balance']:,.2f}, "
                            f"which remains at or above the minimum "
                            f"reserve of ₹{scenario['minimum_reserve']:,.2f}. "
                            "No reserve breach occurs under the "
                            "current assumptions."
                        )

            st.markdown("#### Verified scenario facts")
            st.write(
                f"Lowest projected balance: "
                f"₹{scenario['lowest_balance']:,.2f}"
            )
            st.write(
                f"Projected ending balance: "
                f"₹{scenario['ending_balance']:,.2f}"
            )

            if scenario["reserve_breached"]:
                st.warning(
                    "Minimum reserve breached on "
                    f"{scenario['first_shortfall']}."
                )
            else:
                st.success(
                    "No minimum-reserve breach detected "
                    "within the selected horizon."
                )

            st.markdown("#### AI interpretation")
            st.write(explanation)
            st.caption(
                "AI-generated interpretation may contain errors. "
                "Use the Python-calculated scenario facts above "
                "for the numerical results."
            )

        except (requests.RequestException, KeyError, ValueError) as exc:
            st.error(
                "The local AI service is unavailable or returned "
                "an invalid response. The scenario calculations "
                "above remain available."
            )
            st.caption(str(exc))





    # ============================================
    # INTERACTIVE USD SCENARIO PLANNER
    # ============================================

    st.divider()
    st.header("Interactive USD Scenario Planner")

    st.caption(
        "Plan future USD receipts and expenses using your own "
        "assumptions. This planner does not create PayPal payments "
        "or change your saved Sandbox transactions."
    )

    if "usd_planned_events" not in st.session_state:
        st.session_state.usd_planned_events = []

    # STEP 1: PLANNING ASSUMPTIONS
    with st.container(border=True):
        st.subheader("1. Set your USD planning assumptions")

        u1, u2, u3 = st.columns(3)

        with u1:
            usd_opening = st.number_input(
                "Assumed opening cash balance (USD)",
                min_value=0.0,
                value=250.0,
                step=50.0,
                key="usd_scenario_opening",
            )

        with u2:
            usd_reserve = st.number_input(
                "Minimum cash reserve (USD)",
                min_value=0.0,
                value=200.0,
                step=50.0,
                key="usd_scenario_reserve",
            )

        with u3:
            usd_days = st.selectbox(
                "USD planning horizon",
                [7, 14, 30],
                key="usd_scenario_days",
            )

    # STEP 2: PLANNED CASH MOVEMENTS
    with st.container(border=True):
        st.subheader("2. Add expected USD cash movements")

        with st.form("usd_event_form", clear_on_submit=True):
            u4, u5 = st.columns(2)

            with u4:
                usd_event_type = st.selectbox(
                    "Transaction type",
                    ["Income", "Expense"],
                    key="usd_event_type",
                )

                usd_event_amount = st.number_input(
                    "Expected amount (USD)",
                    min_value=0.01,
                    value=100.0,
                    step=10.0,
                    key="usd_event_amount",
                )

            with u5:
                usd_event_category = st.text_input(
                    "Description",
                    placeholder="Customer payment, supplier, subscription...",
                    key="usd_event_category",
                )

                usd_event_date = st.date_input(
                    "Expected transaction date",
                    value=date.today() + timedelta(days=1),
                    min_value=date.today() + timedelta(days=1),
                    key="usd_event_date",
                )

            usd_add = st.form_submit_button(
                "Add USD planned transaction"
            )

        if usd_add:
            if not usd_event_category.strip():
                st.error("Please enter a transaction description.")
            else:
                st.session_state.usd_planned_events.append({
                    "date": usd_event_date.isoformat(),
                    "type": usd_event_type,
                    "category": usd_event_category.strip(),
                    "amount": float(usd_event_amount),
                })
                st.rerun()

        if st.session_state.usd_planned_events:

            with st.expander(
                f"View planned USD transactions "
                f"({len(st.session_state.usd_planned_events)})",
                expanded=False,
            ):

                for index, event in enumerate(
                    st.session_state.usd_planned_events
                ):

                    row1, row2 = st.columns([5, 1])

                    with row1:
                        st.write(
                            f"{event['date']} · "
                            f"{event['category']} · "
                            f"{event['type']} · "
                            f"${event['amount']:,.2f}"
                        )

                    with row2:
                        if st.button(
                            "Remove",
                            key=f"remove_usd_{index}",
                        ):
                            st.session_state.usd_planned_events.pop(index)
                            st.rerun()

            if st.button(
                "Clear USD planned transactions",
                key="clear_usd_events",
            ):
                st.session_state.usd_planned_events = []
                st.rerun()

        else:
            st.info(
                "Add an expected USD income or expense "
                "to start your scenario."
            )

    # SAVE / LOAD USD SCENARIOS
    with st.container(border=True):
        st.subheader("Save or load a USD scenario")

        usd_scenario_name = st.text_input(
            "Scenario name",
            placeholder="November USD Cash Flow Plan",
            key="usd_save_name",
        )

        if st.button("Save USD Scenario", key="save_usd"):
            try:
                scenario_id = save_scenario(
                    name=usd_scenario_name,
                    currency="USD",
                    opening_balance=usd_opening,
                    minimum_reserve=usd_reserve,
                    planning_days=usd_days,
                    events=[
                        {
                            "date": event["date"],
                            "type": event["type"],
                            "description": event["category"],
                            "amount": event["amount"],
                        }
                        for event in st.session_state.usd_planned_events
                    ],
                )
                st.success(
                    f"USD scenario saved successfully! ID: {scenario_id}"
                )
            except (ValueError, KeyError) as exc:
                st.error(f"Could not save USD scenario: {exc}")

        saved_usd = list_saved_scenarios("USD")

        if saved_usd:
            usd_options = {
                f"{item['name']} (ID {item['id']})": item["id"]
                for item in saved_usd
            }

            selected_usd = st.selectbox(
                "Select a saved USD scenario",
                options=list(usd_options.keys()),
                key="selected_usd_scenario",
            )

            st.button(
                "Load USD Scenario",
                key="load_usd",
                on_click=restore_saved_scenario,
                args=(usd_options[selected_usd], "USD"),
            )
        else:
            st.caption("No saved USD scenarios yet.")

    # STEP 3: DETERMINISTIC FORECAST
    usd_scenario = calculate_scenario(
        opening_balance=usd_opening,
        minimum_reserve=usd_reserve,
        horizon_days=usd_days,
        planned_events=st.session_state.usd_planned_events,
    )

    st.subheader("3. Your projected USD cash position")

    um1, um2, um3 = st.columns(3)

    um1.metric(
        "Projected ending balance",
        f"${usd_scenario['ending_balance']:,.2f}",
    )

    lowest_usd = usd_scenario["lowest_balance"]

    with um2:
        st.markdown("**Lowest projected balance**")

        balance_color = (
            "#FF6B6B" if lowest_usd < 0 else "#4ADEAE"
        )

        st.markdown(
            f"""
            <div style="
                color: {balance_color};
                font-size: 38px;
                font-weight: 750;
                line-height: 1.3;
            ">
                ${lowest_usd:,.2f}
            </div>
            """,
            unsafe_allow_html=True,
        )

    um3.metric(
        "Minimum cash reserve",
        f"${usd_scenario['minimum_reserve']:,.2f}",
    )

    # USD CASH RESERVE WARNING
    usd_lowest = usd_scenario["lowest_balance"]
    usd_minimum = usd_scenario["minimum_reserve"]

    usd_shortfall = max(0.0, usd_minimum - usd_lowest)

    if usd_shortfall > 0:
        st.error(
            f"Cash reserve warning: Your projected balance "
            f"falls ${usd_shortfall:,.2f} below your "
            f"minimum reserve of ${usd_minimum:,.2f}."
        )

        st.info(
            f"Suggested action: Consider collecting "
            f"${usd_shortfall:,.2f} earlier, delaying "
            f"an expense, or arranging sufficient "
            f"short-term funds before the shortfall occurs."
        )
    else:
        st.success(
            "Your projected cash balance remains "
            "at or above your minimum reserve."
        )

    # STEP 4: INTERACTIVE GRAPH
    usd_chart = go.Figure()

    # STEP 4: INTERACTIVE GRAPH
    usd_chart = go.Figure()

    usd_chart.add_trace(
        go.Scatter(
            x=[r["Date"] for r in usd_scenario["forecast"]],
            y=[
                r["Projected Balance"]
                for r in usd_scenario["forecast"]
            ],
            mode="lines+markers",
            line=dict(color="#4ADEAE", width=4),
            marker=dict(color="#4ADEAE", size=9),
            fill="tozeroy",
            fillcolor="rgba(74,222,174,0.08)",
            name="Projected USD cash balance",
            hovertemplate="%{x}<br>$%{y:,.2f}<extra></extra>",
        )
    )

    usd_chart.add_hline(
        y=usd_reserve,
        line_dash="dash",
        line_color="#F5B95C",
        annotation_text="Minimum reserve",
        annotation_font_color="#F5B95C",
    )

    usd_chart.update_layout(
        title="Daily USD Cash-Flow Scenario",
        paper_bgcolor="#17263A",
        plot_bgcolor="#17263A",
        font=dict(color="#E8F0FA", size=17),
        xaxis=dict(
            title="Date",
            showgrid=False,
            tickfont=dict(size=15),
        ),
        yaxis=dict(
            title="Projected cash balance (USD)",
            gridcolor="#304258",
            tickprefix="$",
            tickfont=dict(size=15),
        ),
        height=460,
        margin=dict(l=35, r=35, t=75, b=40),
        showlegend=False,
        hovermode="x unified",
    )

    st.plotly_chart(
        usd_chart,
        use_container_width=True,
        config={"displaylogo": False},
    )

    # STEP 5: RISK ASSESSMENT
    st.subheader("4. USD cash-flow risk assessment")

    if usd_scenario["reserve_breached"]:
        st.warning(
            "Minimum reserve warning: projected USD cash "
            f"falls below ${usd_reserve:,.2f} "
            f"on {usd_scenario['first_shortfall']}."
        )
    else:
        st.success(
            "Projected USD cash stays at or above "
            "your minimum reserve under these assumptions."
        )

    # STEP 6: AI EXPLANATION
    st.subheader("5. AI-assisted USD financial explanation")

    if st.button(
        "Explain USD scenario with Clearflow AI",
        key="explain_usd_scenario",
    ):
        import json
        import requests

        verified_usd_facts = {
            "currency": "USD",
            "opening_balance": usd_scenario["opening_balance"],
            "ending_balance": usd_scenario["ending_balance"],
            "lowest_balance": usd_scenario["lowest_balance"],
            "minimum_reserve": usd_scenario["minimum_reserve"],
            "first_shortfall": usd_scenario["first_shortfall"],
            "reserve_breached": usd_scenario["reserve_breached"],
            "planned_events": st.session_state.usd_planned_events,
        }

        system_prompt = (
            "You are Clearflow's USD financial scenario explainer. "
            "The provided JSON contains Python-calculated results. "
            "Never change the verified numbers. "
            "Explain the timing of receipts and expenses, "
            "identify reserve risks, and recommend practical "
            "actions for a small-business owner. "
            "Do not claim these are actual PayPal payments "
            "or verified account balances. "
            "Avoid unnecessary borrowing recommendations. "
            "Keep the explanation concise."
        )

        try:
            with st.spinner("Analysing USD scenario..."):
                response = requests.post(
                    "http://127.0.0.1:11434/api/chat",
                    json={
                        "model": "qwen2.5:3b",
                        "stream": False,
                        "messages": [
                            {
                                "role": "system",
                                "content": system_prompt,
                            },
                            {
                                "role": "user",
                                "content": json.dumps(
                                    verified_usd_facts
                                ),
                            },
                        ],
                    },
                    timeout=120,
                )

                response.raise_for_status()

                usd_explanation = response.json()[
                    "message"
                ]["content"]

            st.markdown("#### Verified USD scenario facts")
            st.write(
                f"Lowest projected balance: "
                f"${usd_scenario['lowest_balance']:,.2f}"
            )
            st.write(
                f"Projected ending balance: "
                f"${usd_scenario['ending_balance']:,.2f}"
            )

            st.markdown("#### AI interpretation")
            st.write(usd_explanation)

            st.caption(
                "AI-generated explanations may contain errors. "
                "USD scenarios are hypothetical and separate "
                "from actual PayPal Sandbox captures."
            )

        except (requests.RequestException, KeyError, ValueError) as exc:
            st.error(
                "The local AI service is unavailable or "
                "returned an invalid response."
            )
            st.caption(str(exc))

    st.info(
        "USD scenarios are based entirely on user assumptions. "
        "They do not represent actual PayPal balances or "
        "guaranteed future receipts."
    )

    st.info(
        "Historical PayPal Sandbox captures are shown as evidence "
        "of past payment activity. Future balances depend on the "
        "assumptions entered above and are not guaranteed."
    )


elif page == 'Money Activity':
    st.subheader('INR transaction ledger')
    st.caption(
        'Review synthetic INR transactions. '
        'Only manually added transactions can be deleted.'
    )

    if not transactions:
        st.info('No transactions available.')

    for t in transactions:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])

            col1.write(str(t["Date"]))
            col2.write(f'{t["Category"]} ({t["Type"]})')
            col3.write(f'₹{t["Amount"]:,.2f}')

            # Deletion is enforced by the database function.
            transaction_id = t["ID"]

            if col4.button(
                'Delete',
                key=f'delete_{transaction_id}'
            ):
                st.session_state[
                    'pending_delete_id'
                ] = transaction_id

            if st.session_state.get(
                'pending_delete_id'
            ) == transaction_id:
                st.warning(
                    f'Permanently delete {t["Category"]} '
                    f'(₹{t["Amount"]:,.2f})?'
                )

                confirm_col, cancel_col = st.columns(2)

                if confirm_col.button(
                    'Confirm deletion',
                    key=f'confirm_{transaction_id}'
                ):
                    deleted = delete_transaction(transaction_id)
                    st.session_state.pop('pending_delete_id', None)

                    if deleted:
                        st.success('Transaction deleted.')
                    else:
                        st.error(
                            'Transaction could not be deleted. '
                            'Only manually entered INR records '
                            'are eligible.'
                        )

                    st.rerun()

                if cancel_col.button(
                    'Cancel',
                    key=f'cancel_{transaction_id}'
                ):
                    st.session_state.pop('pending_delete_id', None)
                    st.rerun()

    st.subheader('Add transaction')

    with st.form('new_transaction_form'):
        date = st.date_input('Transaction date')
        transaction_type = st.selectbox(
            'Transaction type', ['Income', 'Expense']
        )
        category = st.text_input(
            'Category',
            placeholder='Sales, Rent, Supplies...'
        )
        transaction_amount = st.number_input(
            'Amount (INR)',
            min_value=1.0,
            value=1000.0,
            step=100.0
        )

        submitted = st.form_submit_button('Save transaction')

        if submitted:
            try:
                add_transaction(
                    date,
                    transaction_type,
                    category,
                    transaction_amount
                )
                st.success('Transaction saved successfully.')
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

st.divider()
st.caption('Clearflow · PayPal AI Hackathon 2026 · Sandbox demonstration')
