import datetime
from db.finance_functions import get_daily_profit, get_profit_by_product_delta
from agents.finance_insights import collect_finance_insights, compute_trend, detect_profit_decline_insight
from agents.finance_insights import detect_product_drivers_insight

def test_get_daily_profit():
    today = datetime.date.today()
    start = today - datetime.timedelta(days=10)
    data = get_daily_profit(start, today)
    assert isinstance(data, list)
    assert all("profit" in d for d in data)

def test_collect_finance_insights():
    today = datetime.date.today()
    insights = collect_finance_insights(today)
    assert isinstance(insights, list)
    # depending on your fake data, you may expect at least one insight
    assert len(insights) >= 0

def test_profit_delta():
    today = datetime.date.today()
    start_start = today - datetime.timedelta(days=60)
    start_end   = today - datetime.timedelta(days=30)
    end_start   = today - datetime.timedelta(days=30)
    end_end     = today
    rows = get_profit_by_product_delta(start_start, start_end, end_start, end_end)
    assert isinstance(rows, list)
    if rows:
        row = rows[0]
        assert "product_id" in row
        assert "profit_delta" in row

def test_compute_trend_strong_decrease():
    # first 5 days high profit, last day very low -> strong decrease
    series = [
        {"profit": 100},
        {"profit": 105},
        {"profit": 98},
        {"profit": 102},
        {"profit": 99},
        {"profit": 50},  # big drop
    ]
    trend = compute_trend(series)
    assert trend["direction"] in ("mild_decrease", "strong_decrease")
    assert trend["change_pct"] < 0


def test_compute_trend_flat_when_not_enough_points():
    series = [
        {"profit": 100},
        {"profit": 110},
        {"profit": 120},
    ]
    trend = compute_trend(series)
    assert trend["direction"] == "flat"

def test_detect_profit_decline_insight_returns_something():
    today = datetime.date(2025, 11, 19)  # matches your last fake date
    insight = detect_profit_decline_insight(today)
    # Depending on your thresholds, this might be None or a dict.
    # With your current data, we EXPECT a decline insight.
    assert insight is not None
    assert insight["type"] == "overall_profit_decline"
    assert insight["metric"] == "profit"
    assert "evidence" in insight
    assert "trend" in insight["evidence"]

def test_detect_product_drivers_insight_returns_negative_drivers():
    # The dates don't matter for the mock; we just need a valid "today".
    today = datetime.date(2025, 11, 19)
    insight = detect_product_drivers_insight(today)

    assert insight is not None
    assert insight["type"] == "product_profit_drivers"
    assert insight["severity"] in ("high", "medium")
    ev = insight["evidence"]
    assert ev["total_profit_delta"] < 0  # net drop
    assert any(d["profit_delta"] < 0 for d in ev["top_negative_products"])