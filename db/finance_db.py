# db/finance_db.py
import os
import sqlite3
import datetime
from typing import Dict, Any, Iterable
from pathlib import Path

# DB_PATH = os.getenv("FINANCE_DB_PATH", "finance.db")
# Put the DB file next to this module by default
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("FINANCE_DB_PATH", BASE_DIR / "finance.db"))

def get_connection() -> sqlite3.Connection:
    """
    Returns a new SQLite connection.
    row_factory is set to sqlite3.Row so we can read by column name.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Create tables if they don't exist.
    Call this once at finance service startup.
    """
    conn = get_connection()
    cur = conn.cursor()

    # One row per day (can also aggregate multiple docs per day if you want)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_financials (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            date     TEXT NOT NULL,         -- 'YYYY-MM-DD'
            revenue  REAL NOT NULL,
            cost     REAL NOT NULL,
            profit   REAL NOT NULL
        );
        """
    )

    # One row per product per day
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS product_financials (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            date          TEXT NOT NULL,    -- 'YYYY-MM-DD'
            product_id    TEXT NOT NULL,
            product_name  TEXT NOT NULL,
            revenue       REAL NOT NULL,
            cost          REAL NOT NULL,
            profit        REAL NOT NULL
        );
        """
    )

    conn.commit()
    conn.close()


# ---------- WRITE HELPERS (insert / update) ----------

def upsert_daily_financial(
    date: datetime.date,
    revenue: float,
    cost: float,
) -> None:
    """
    Insert or update daily_financials for a given date.
    If a row for that date exists, we replace it (simple version).
    """
    profit = revenue - cost
    ds = date.isoformat()

    conn = get_connection()
    cur = conn.cursor()

    # Check if exists
    cur.execute("SELECT id FROM daily_financials WHERE date = ?", (ds,))
    row = cur.fetchone()

    if row:
        cur.execute(
            """
            UPDATE daily_financials
            SET revenue = ?, cost = ?, profit = ?
            WHERE date = ?
            """,
            (revenue, cost, profit, ds),
        )
    else:
        cur.execute(
            """
            INSERT INTO daily_financials (date, revenue, cost, profit)
            VALUES (?, ?, ?, ?)
            """,
            (ds, revenue, cost, profit),
        )

    conn.commit()
    conn.close()


def add_product_financial(
    date: datetime.date,
    product_id: str,
    product_name: str,
    revenue: float,
    cost: float,
) -> None:
    """
    Insert a new row into product_financials.
    If you want upsert per (date, product_id) you can adapt it.
    """
    profit = revenue - cost
    ds = date.isoformat()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO product_financials
            (date, product_id, product_name, revenue, cost, profit)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (ds, product_id, product_name, revenue, cost, profit),
    )
    conn.commit()
    conn.close()
