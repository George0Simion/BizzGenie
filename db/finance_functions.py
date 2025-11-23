# db/finance_functions.py
"""
Real DB implementation for finance.

Uses SQLite via finance_db.py, but keeps the same public functions
that finance_insights.py expects:
- get_daily_profit
- get_profit_by_product
- get_profit_by_product_delta
"""

import datetime
from typing import List, Dict

from db.finance_db import get_connection


def get_daily_profit(
    start_date: datetime.date,
    end_date: datetime.date,
) -> List[Dict]:
    """
    Returns:
    [
      {"date": date, "revenue": float, "cost": float, "profit": float},
      ...
    ]
    """
    start_s = start_date.isoformat()
    end_s = end_date.isoformat()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT date, SUM(revenue) AS revenue,
               SUM(cost)    AS cost,
               SUM(profit)  AS profit
        FROM daily_financials
        WHERE date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date ASC
        """,
        (start_s, end_s),
    )

    rows = cur.fetchall()
    conn.close()

    result: List[Dict] = []
    for r in rows:
        d = datetime.date.fromisoformat(r["date"])
        result.append(
            {
                "date": d,
                "revenue": float(r["revenue"] or 0.0),
                "cost": float(r["cost"] or 0.0),
                "profit": float(r["profit"] or 0.0),
            }
        )
    return result


def get_profit_by_product(
    start_date: datetime.date,
    end_date: datetime.date,
    top_n: int = 20,
) -> List[Dict]:
    """
    Returns products sorted by profit desc:
    [
      {
        "product_id": "...",
        "product_name": "...",
        "revenue": float,
        "cost": float,
        "profit": float,
      },
      ...
    ]
    """
    start_s = start_date.isoformat()
    end_s = end_date.isoformat()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            product_id,
            product_name,
            SUM(revenue) AS revenue,
            SUM(cost)    AS cost,
            SUM(profit)  AS profit
        FROM product_financials
        WHERE date BETWEEN ? AND ?
        GROUP BY product_id, product_name
        ORDER BY profit DESC
        LIMIT ?
        """,
        (start_s, end_s, top_n),
    )

    rows = cur.fetchall()
    conn.close()

    result: List[Dict] = []
    for r in rows:
        result.append(
            {
                "product_id": r["product_id"],
                "product_name": r["product_name"],
                "revenue": float(r["revenue"] or 0.0),
                "cost": float(r["cost"] or 0.0),
                "profit": float(r["profit"] or 0.0),
            }
        )
    return result


def _aggregate_product_profit(
    start_date: datetime.date, end_date: datetime.date
) -> Dict[str, Dict]:
    """
    Helper: returns dict[product_id] -> {product_id, product_name, profit}
    for the given period.
    """
    start_s = start_date.isoformat()
    end_s = end_date.isoformat()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            product_id,
            product_name,
            SUM(profit) AS profit
        FROM product_financials
        WHERE date BETWEEN ? AND ?
        GROUP BY product_id, product_name
        """,
        (start_s, end_s),
    )

    rows = cur.fetchall()
    conn.close()

    out: Dict[str, Dict] = {}
    for r in rows:
        pid = r["product_id"]
        out[pid] = {
            "product_id": pid,
            "product_name": r["product_name"],
            "profit": float(r["profit"] or 0.0),
        }
    return out


def get_profit_by_product_delta(
    start_start: datetime.date,
    start_end: datetime.date,
    end_start: datetime.date,
    end_end: datetime.date,
    top_n: int = 20,
) -> List[Dict]:
    """
    Compare two periods and return products sorted by profit_delta (end - start):
    [
      {
        "product_id": "...",
        "product_name": "...",
        "profit_period1": float,
        "profit_period2": float,
        "profit_delta": float,
      },
      ...
    ]
    """
    p1 = _aggregate_product_profit(start_start, start_end)
    p2 = _aggregate_product_profit(end_start, end_end)

    all_ids = set(p1.keys()) | set(p2.keys())
    rows: List[Dict] = []

    for pid in all_ids:
        name = (p2.get(pid) or p1.get(pid))["product_name"]
        profit1 = p1.get(pid, {}).get("profit", 0.0)
        profit2 = p2.get(pid, {}).get("profit", 0.0)
        delta = profit2 - profit1

        rows.append(
            {
                "product_id": pid,
                "product_name": name,
                "profit_period1": float(profit1),
                "profit_period2": float(profit2),
                "profit_delta": float(delta),
            }
        )

    rows.sort(key=lambda r: r["profit_delta"])  # most negative first
    return rows[:top_n]
