
from datetime import date, timedelta


def generate_forecast(transactions, days=7, opening_balance=0):
    """
    Simple run-rate forecast using synthetic historical data.
    This is a baseline projection, not a trained ML forecast.
    """
    if not transactions:
        return []

    dates = [
        date.fromisoformat(t["Date"])
        for t in transactions
    ]

    period_days = max((max(dates) - min(dates)).days + 1, 1)

    income = sum(
        t["Amount"] for t in transactions
        if t["Type"] == "Income"
    )
    expenses = sum(
        t["Amount"] for t in transactions
        if t["Type"] == "Expense"
    )

    daily_net = (income - expenses) / period_days

    # Opening balance is a user-supplied assumption.
    balance = float(opening_balance)
    results = []

    for day in range(1, days + 1):
        balance += daily_net
        results.append({
            "Date": (date.today() + timedelta(days=day)).isoformat(),
            "Projected Balance": round(balance, 2)
        })

    return results
