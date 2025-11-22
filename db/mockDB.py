from typing import List, Dict
import datetime

# ---- fake data ----

# Daily financials for last ~10 days
_FAKE_DAILY = [
    # date, revenue, cost
    ("2025-11-10", 1000, 700),
    ("2025-11-11", 1100, 750),
    ("2025-11-12", 900,  700),
    ("2025-11-13", 950,  720),
    ("2025-11-14", 800,  650),
    ("2025-11-15", 780,  640),
    ("2025-11-16", 750,  650),
    ("2025-11-17", 730,  660),
    ("2025-11-18", 700,  670),
    ("2025-11-19", 690,  680),
]

# Product-level profit for two periods (prev vs current)
# product_id, name, profit_prev, profit_curr
_FAKE_PRODUCT_DELTA = [
    ("burger", "Burger clasic",      4000, 2500),  # big drop
    ("pizza",  "Pizza Margherita",   3000, 3200),  # small increase
    ("pasta",  "Penne Alfredo",      2000, 1500),  # drop
    ("salad",  "Salată grecească",   1000, 900),   # small drop
    ("soda",   "Suc la pahar",        800, 900),   # increase
]

def _parse_date(s: str) -> datetime.date:
    return datetime.date.fromisoformat(s)

def get_daily_profit(start_date: datetime.date,
                     end_date: datetime.date) -> List[Dict]:
    """
    Mock version: filter the fake daily list by date.
    """
    result = []
    for ds, revenue, cost in _FAKE_DAILY:
        d = _parse_date(ds)
        if start_date <= d <= end_date:
            profit = revenue - cost
            result.append({
                "date": d,
                "revenue": float(revenue),
                "cost": float(cost),
                "profit": float(profit),
            })
    # sort by date just in case
    result.sort(key=lambda r: r["date"])
    return result

def get_profit_by_product(start_date: datetime.date,
                          end_date: datetime.date,
                          top_n: int = 20) -> List[Dict]:
    """
    Mock version: just pretend 'current period' is _FAKE_PRODUCT_DELTA.curr.
    Ignores dates, returns top_n by profit descending.
    """
    rows = [
        {
            "product_id": pid,
            "product_name": name,
            "revenue": 0.0,   # you can fake this too if you care
            "cost": 0.0,
            "profit": float(profit_curr),
        }
        for (pid, name, profit_prev, profit_curr) in _FAKE_PRODUCT_DELTA
    ]
    rows.sort(key=lambda r: r["profit"], reverse=True)
    return rows[:top_n]

def get_profit_by_product_delta(
    start_start: datetime.date, start_end: datetime.date,
    end_start: datetime.date, end_end: datetime.date,
    top_n: int = 20
) -> List[Dict]:
    """
    Mock version: uses _FAKE_PRODUCT_DELTA directly and returns the delta.
    Ignores actual dates.
    """
    rows = []
    for (pid, name, profit_prev, profit_curr) in _FAKE_PRODUCT_DELTA:
        delta = profit_curr - profit_prev
        rows.append({
            "product_id": pid,
            "product_name": name,
            "profit_period1": float(profit_prev),
            "profit_period2": float(profit_curr),
            "profit_delta": float(delta),
        })
    # sort by most negative delta first
    rows.sort(key=lambda r: r["profit_delta"])
    return rows[:top_n]