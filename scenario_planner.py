
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP


def money(value):
    return Decimal(str(value)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def calculate_scenario(
    opening_balance,
    minimum_reserve,
    horizon_days,
    planned_events,
    start_date=None,
):
    """Calculate future balances from explicitly planned events."""
    if start_date is None:
        start_date = date.today()

    opening = money(opening_balance)
    reserve = money(minimum_reserve)

    if opening < 0 or reserve < 0:
        raise ValueError("Balances and reserves cannot be negative.")

    if horizon_days not in (7, 14, 30):
        raise ValueError("Choose a 7-, 14-, or 30-day horizon.")

    daily_changes = {}

    for event in planned_events:
        event_date = date.fromisoformat(str(event["date"]))
        amount = money(event["amount"])
        event_type = event["type"]

        if amount <= 0:
            raise ValueError("Planned amounts must be positive.")

        if event_type not in ("Income", "Expense"):
            raise ValueError("Invalid planned transaction type.")

        signed_amount = amount if event_type == "Income" else -amount

        daily_changes[event_date] = (
            daily_changes.get(event_date, Decimal("0"))
            + signed_amount
        )

    balance = opening
    rows = []
    lowest_balance = opening
    first_shortfall = None

    for offset in range(horizon_days + 1):
        current_date = start_date + timedelta(days=offset)

        balance += daily_changes.get(
            current_date, Decimal("0")
        )

        balance = money(balance)
        lowest_balance = min(lowest_balance, balance)

        if balance < reserve and first_shortfall is None:
            first_shortfall = current_date.isoformat()

        rows.append({
            "Date": current_date.isoformat(),
            "Projected Balance": float(balance),
        })

    return {
        "forecast": rows,
        "opening_balance": float(opening),
        "ending_balance": float(balance),
        "lowest_balance": float(lowest_balance),
        "minimum_reserve": float(reserve),
        "first_shortfall": first_shortfall,
        "reserve_breached": first_shortfall is not None,
    }
