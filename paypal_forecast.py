
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP


def generate_paypal_forecast(
    payments,
    days=7,
    opening_balance=0.0,
    expected_daily_receipts=0.0,
    expected_daily_expenses=0.0,
):
    """
    Scenario-based USD forecast using verified PayPal
    Sandbox records and user-provided assumptions.

    Historical captured payments are reported separately.
    They are not automatically counted as future receipts.
    """

    if days not in (7, 14, 30):
        raise ValueError("Forecast days must be 7, 14, or 30.")

    def money(value):
        return Decimal(str(value)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    opening = money(opening_balance)
    daily_receipts = money(expected_daily_receipts)
    daily_expenses = money(expected_daily_expenses)

    if min(opening, daily_receipts, daily_expenses) < 0:
        raise ValueError("Forecast inputs cannot be negative.")

    completed_count = 0
    captured_total = Decimal("0.00")
    pending_count = 0

    for payment in payments:
        if payment.get("currency") != "USD":
            continue

        status = str(payment.get("status", "")).upper()

        if status == "COMPLETED" and payment.get("capture_id"):
            completed_count += 1
            captured_total += money(payment.get("amount", 0))
        elif status != "COMPLETED":
            pending_count += 1

    balance = opening
    forecast = []

    for day in range(1, days + 1):
        balance += daily_receipts - daily_expenses

        forecast.append({
            "Date": (
                date.today() + timedelta(days=day)
            ).isoformat(),
            "Projected Balance": float(balance),
        })

    return {
        "completed_count": completed_count,
        "historical_captured_usd": float(captured_total),
        "pending_count": pending_count,
        "projected_ending_balance_usd": float(balance),
        "forecast": forecast,
        "assumptions": {
            "opening_balance_usd": float(opening),
            "expected_daily_receipts_usd": float(daily_receipts),
            "expected_daily_expenses_usd": float(daily_expenses),
        },
    }
