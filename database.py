
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


def get_transactions():
    with connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT date, type, category, amount
            FROM transactions
            WHERE currency = 'INR'
            ORDER BY date, id
        """).fetchall()

    return [
        {
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
        conn.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )