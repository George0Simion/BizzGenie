import datetime
from typing import List, Dict

# Fake data for Finance
_FAKE_DAILY = [
    ("2025-11-10", 1000, 700), ("2025-11-11", 1100, 750), ("2025-11-12", 900,  700),
    ("2025-11-13", 950,  720), ("2025-11-14", 800,  650), ("2025-11-15", 780,  640),
    ("2025-11-16", 750,  650), ("2025-11-17", 730,  660), ("2025-11-18", 700,  670),
    ("2025-11-19", 690,  680),
]

_FAKE_PRODUCT_DELTA = [
    ("burger", "Burger clasic",      4000, 2500),
    ("pizza",  "Pizza Margherita",   3000, 3200),
    ("pasta",  "Penne Alfredo",      2000, 1500),
    ("salad",  "Salată grecească",   1000, 900),
    ("soda",   "Suc la pahar",        800, 900),
]

def _parse_date(s: str) -> datetime.date:
    return datetime.date.fromisoformat(s)

def get_daily_profit(start_date: datetime.date, end_date: datetime.date) -> List[Dict]:
    result = []
    for ds, revenue, cost in _FAKE_DAILY:
        d = _parse_date(ds)
        if start_date <= d <= end_date:
            result.append({
                "date": d, "revenue": float(revenue), "cost": float(cost), "profit": float(revenue - cost),
            })
    return sorted(result, key=lambda r: r["date"])

def get_profit_by_product(start_date, end_date, top_n=20):
    rows = [{"product_id": pid, "product_name": name, "profit": float(curr)} 
            for (pid, name, prev, curr) in _FAKE_PRODUCT_DELTA]
    rows.sort(key=lambda r: r["profit"], reverse=True)
    return rows[:top_n]

def get_profit_by_product_delta(start_start, start_end, end_start, end_end, top_n=20):
    rows = []
    for (pid, name, prev, curr) in _FAKE_PRODUCT_DELTA:
        rows.append({
            "product_id": pid, "product_name": name,
            "profit_period1": float(prev), "profit_period2": float(curr),
            "profit_delta": float(curr - prev),
        })
    rows.sort(key=lambda r: r["profit_delta"])
    return rows[:top_n]