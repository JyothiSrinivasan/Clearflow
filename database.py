
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "clearflow.db"

DEMO_TRANSACTIONS = [
    ("2026-11-01", "Income", "Sales", 15000),
    ("2026-11-02", "Expense", "Supplies", 4500),
    ("2026-11-03", "Income", "Services", 22000),
    ("2026-11-04", "Expense", "Rent", 8000),
    ("2026-11-05", "Income", "Sales", 12500),
]


def connect():
    return sqlite3.connect(DB_PATH, timeout=10)


def init_database():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL
                    CHECK (type IN ('Income', 'Expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                currency TEXT NOT NULL DEFAULT 'INR',
                source TEXT NOT NULL DEFAULT 'demo'
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0]

        # Seed sample data only on first initialization.
        if count == 0:
            conn.executemany("""
                INSERT INTO transactions
                (date, type, category, amount, currency, source)
                VALUES (?, ?, ?, ?, 'INR', 'demo')
            """, DEMO_TRANSACTIONS)

                # Saved financial planning scenarios
        conn.execute("""
            CREATE TABLE IF NOT EXISTS saved_scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                currency TEXT NOT NULL
                    CHECK (currency IN ('INR', 'USD')),
                opening_balance REAL NOT NULL,
                minimum_reserve REAL NOT NULL,
                planning_days INTEGER NOT NULL,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Planned transactions belonging to saved scenarios
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scenario_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER NOT NULL,
                event_date TEXT NOT NULL,
                event_type TEXT NOT NULL
                    CHECK (event_type IN ('Income', 'Expense')),
                description TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                FOREIGN KEY (scenario_id)
                    REFERENCES saved_scenarios(id)
                    ON DELETE CASCADE
            )
        """)



def get_transactions():
    with connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT id, date, type, category, amount
            FROM transactions
            WHERE currency = 'INR'
            ORDER BY date DESC, id DESC
        """).fetchall()

    return [
        {
            "ID": row["id"],
            "Date": row["date"],
            "Type": row["type"],
            "Category": row["category"],
            "Amount": row["amount"]
        }
        for row in rows
    ]



def add_transaction(date, type_, category, amount):
    if type_ not in ("Income", "Expense"):
        raise ValueError("Invalid transaction type.")

    if not category.strip() or amount <= 0:
        raise ValueError("Category and positive amount required.")

    with connect() as conn:
        conn.execute("""
            INSERT INTO transactions
            (date, type, category, amount, currency, source)
            VALUES (?, ?, ?, ?, 'INR', 'manual')
        """, (
            str(date),
            type_,
            category.strip(),
            float(amount)
        ))

def delete_transaction(transaction_id):
    with connect() as conn:
        cursor = conn.execute("""
            DELETE FROM transactions
            WHERE id = ?
              AND currency = 'INR'
              AND source = 'manual'
        """, (int(transaction_id),))

        return cursor.rowcount > 0

def save_scenario(
    name,
    currency,
    opening_balance,
    minimum_reserve,
    planning_days,
    events,
):
    name = name.strip()

    if not name:
        raise ValueError("Scenario name is required.")

    if currency not in ("INR", "USD"):
        raise ValueError("Currency must be INR or USD.")

    if opening_balance < 0 or minimum_reserve < 0:
        raise ValueError("Balances cannot be negative.")

    if planning_days not in (7, 14, 30):
        raise ValueError("Invalid planning horizon.")

    with connect() as conn:
        cursor = conn.execute("""
            INSERT INTO saved_scenarios
            (name, currency, opening_balance,
             minimum_reserve, planning_days)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            currency,
            float(opening_balance),
            float(minimum_reserve),
            int(planning_days),
        ))

        scenario_id = cursor.lastrowid

        for event in events:
            event_type = event["type"]
            amount = float(event["amount"])

            if event_type not in ("Income", "Expense"):
                raise ValueError("Invalid event type.")

            if amount <= 0:
                raise ValueError("Event amount must be positive.")

            conn.execute("""
                INSERT INTO scenario_events
                (scenario_id, event_date, event_type,
                 description, amount)
                VALUES (?, ?, ?, ?, ?)
            """, (
                scenario_id,
                str(event["date"]),
                event_type,
                str(event["description"]),
                amount,
            ))

    return scenario_id


def list_saved_scenarios(currency):
    if currency not in ("INR", "USD"):
        raise ValueError("Invalid currency.")

    with connect() as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT id, name, currency, created_at
            FROM saved_scenarios
            WHERE currency = ?
            ORDER BY id DESC
        """, (currency,)).fetchall()

    return [dict(row) for row in rows]


def load_scenario(scenario_id):
    with connect() as conn:
        conn.row_factory = sqlite3.Row

        scenario = conn.execute("""
            SELECT *
            FROM saved_scenarios
            WHERE id = ?
        """, (int(scenario_id),)).fetchone()

        if scenario is None:
            return None

        events = conn.execute("""
            SELECT event_date, event_type,
                   description, amount
            FROM scenario_events
            WHERE scenario_id = ?
            ORDER BY event_date, id
        """, (int(scenario_id),)).fetchall()

    result = dict(scenario)

    result["events"] = [
        {
            "date": row["event_date"],
            "type": row["event_type"],
            "description": row["description"],
            "amount": row["amount"],
        }
        for row in events
    ]

    return result

def init_paypal_database():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS paypal_payments (
                order_id TEXT PRIMARY KEY,
                capture_id TEXT,
                status TEXT NOT NULL,
                amount TEXT NOT NULL,
                currency TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_paypal_payment(payment):
    """Upsert one verified PayPal order; never add USD to the INR ledger."""
    init_paypal_database()
    with connect() as conn:
        conn.execute("""
            INSERT INTO paypal_payments
                (order_id, capture_id, status, amount, currency, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(order_id) DO UPDATE SET
                capture_id=excluded.capture_id,
                status=excluded.status,
                amount=excluded.amount,
                currency=excluded.currency,
                updated_at=CURRENT_TIMESTAMP
        """, (payment['order_id'], payment.get('capture_id'),
              payment['status'], payment['amount'], payment['currency']))


def get_paypal_payments():
    init_paypal_database()
    with connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT order_id, capture_id, status, amount, currency, updated_at
            FROM paypal_payments ORDER BY updated_at DESC, order_id DESC
        """).fetchall()
    return [dict(row) for row in rows]
