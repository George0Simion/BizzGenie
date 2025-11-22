# /agents/finance_insights.py
from typing import List, Dict
import datetime
# from db.finance_functions import get_daily_profit, get_profit_by_product_delta
from db.mockDB import get_daily_profit, get_profit_by_product_delta

def compute_trend(series: List[Dict]) -> Dict:
    """
    Very simple trend: last value vs average of previous N.
    You can replace with linear regression, z-score, etc.
    """
    if len(series) < 5:
        return {"direction": "flat", "severity": 0.0}

    profits = [p["profit"] for p in series]
    recent = profits[-1]
    prev_avg = sum(profits[:-1]) / (len(profits) - 1)
    if prev_avg == 0:
        return {"direction": "flat", "severity": 0.0}

    change_pct = (recent - prev_avg) / abs(prev_avg) * 100

    if change_pct <= -20:
        direction = "strong_decrease"
    elif change_pct <= -5:
        direction = "mild_decrease"
    elif change_pct >= 20:
        direction = "strong_increase"
    elif change_pct >= 5:
        direction = "mild_increase"
    else:
        direction = "flat"

    return {
        "direction": direction,
        "change_pct": change_pct,
        "recent": recent,
        "prev_avg": prev_avg,
    }

def detect_profit_decline_insight(today: datetime.date) -> Dict | None:
    """
    Check last 30 days: if profit trending down, generate an insight object.
    """
    start_date = today - datetime.timedelta(days=30)
    daily = get_daily_profit(start_date, today)
    trend = compute_trend(daily)

    if trend["direction"] not in ("mild_decrease", "strong_decrease"):
        return None

    return {
        "type": "overall_profit_decline",
        "severity": "high" if trend["direction"] == "strong_decrease" else "medium",
        "metric": "profit",
        "time_window": {"start": start_date.isoformat(), "end": today.isoformat()},
        "evidence": {
            "trend": trend,
            "daily_profit": daily[-7:],  # last week as context
        },
    }

def detect_product_drivers_insight(
    today: datetime.date
) -> Dict | None:
    """
    Compare last month vs previous month to see which products drive the change.
    """
    this_month_start = today.replace(day=1)
    prev_month_end = this_month_start - datetime.timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)

    drivers = get_profit_by_product_delta(
        start_start=prev_month_start,
        start_end=prev_month_end,
        end_start=this_month_start,
        end_end=today,
        top_n=10,
    )

    # You can add numerical filtering here (e.g. only if sum of negative deltas is big)
    total_delta = sum(d["profit_delta"] for d in drivers)
    if total_delta >= 0:
        return None  # no net drop driven by products

    return {
        "type": "product_profit_drivers",
        "severity": "high",
        "time_window": {
            "prev_start": prev_month_start.isoformat(),
            "prev_end": prev_month_end.isoformat(),
            "curr_start": this_month_start.isoformat(),
            "curr_end": today.isoformat(),
        },
        "evidence": {
            "total_profit_delta": total_delta,
            "top_negative_products": [
                d for d in drivers if d["profit_delta"] < 0
            ],
            "top_positive_products": [
                d for d in drivers if d["profit_delta"] > 0
            ],
        },
    }

def collect_finance_insights(today: datetime.date) -> List[Dict]:
    """
    This is called by FinanceAgent and by monitor.
    """
    insights: List[Dict] = []

    overall = detect_profit_decline_insight(today)
    if overall:
        insights.append(overall)

    drivers = detect_product_drivers_insight(today)
    if drivers:
        insights.append(drivers)

    # You can add more detectors:
    # - cost increase on an ingredient
    # - drop in average ticket size
    # - etc.

    return insights
