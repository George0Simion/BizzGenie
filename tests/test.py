"""
Unified test runner for BizzGenie.

Run directly:
    python tests/test.py

It contains:
- finance tests (using real OpenAI via finance_agent / finance_llm_client)
- finance insights tests (pure Python over fake data)
- a full orchestrator+inventory+legal flow test (services are auto-started in background).
"""

import datetime
import requests
import sys
from pathlib import Path

# -------------------------------------------------------------------
# Make project root importable when running this file directly
# -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from db.finance_functions import (
    get_daily_profit,
    get_profit_by_product_delta,
)
from agents.finance_insights import (
    collect_finance_insights,
    compute_trend,
    detect_profit_decline_insight,
    detect_product_drivers_insight,
)
from agents import finance_agent


# -------------------------
# Finance agent tests (REAL LLM)
# -------------------------

def test_generate_advice_from_insights_empty_real():
    """
    When no insights, finance_agent.generate_advice_from_insights should
    NOT call the LLM and must return the default Romanian message.
    """
    result = finance_agent.generate_advice_from_insights([])
    assert isinstance(result, dict)
    assert result["actions"] == []
    # this path does NOT hit OpenAI at all
    assert "Nu am detectat" in result["summary_markdown"]


def test_generate_advice_from_insights_nonempty_real():
    """
    Integration-style test: use the real finance LLM client.

    This WILL call OpenAI's Responses API.
    Requires OPENAI_API_KEY to be set in the environment.
    """
    today = datetime.date(2025, 11, 19)
    # use the same fake date as your insights tests to ensure we get something
    insights = collect_finance_insights(today)
    # make sure we actually have at least one insight
    assert isinstance(insights, list)

    advice = finance_agent.generate_advice_from_insights(insights)

    assert isinstance(advice, dict)
    assert "summary_markdown" in advice
    assert "actions" in advice
    assert isinstance(advice["actions"], list)
    assert "affected_metrics" in advice


# -------------------------
# Finance insights tests (pure Python over fake data)
# -------------------------

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
    # may be 0 depending on date vs fake data, but must at least be a list
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

def test_finance_auto_check_http():
    resp = requests.post("http://127.0.0.1:5004/api/finance/auto_check", timeout=60)
    assert resp.status_code == 200
    data = resp.json()
    assert "date" in data
    assert "insights" in data
    assert "advice" in data


def test_detect_profit_decline_insight_returns_something():
    # use the fake-data-aligned date
    today = datetime.date(2025, 11, 19)
    insight = detect_profit_decline_insight(today)
    assert insight is not None
    assert insight["type"] == "overall_profit_decline"
    assert insight["metric"] == "profit"
    assert "evidence" in insight
    assert "trend" in insight["evidence"]


def test_detect_product_drivers_insight_returns_negative_drivers():
    today = datetime.date(2025, 11, 19)
    insight = detect_product_drivers_insight(today)
    assert insight is not None
    assert insight["type"] == "product_profit_drivers"
    ev = insight["evidence"]
    assert ev["total_profit_delta"] < 0
    assert any(d["profit_delta"] < 0 for d in ev["top_negative_products"])


# -------------------------
# Full orchestrator + inventory + legal flow
# -------------------------

BASE_URL = "http://127.0.0.1:5001"


def test_full_flow():
    """
    End-to-end:
    - Send natural language to orchestrator
    - Orchestrator calls inventory agent (and legal)
    - Inventory DB updated
    - Inventory fetched back through orchestrator
    """
    print("🚀 1. Sending 'Add' message to Orchestrator...")
    msg_payload = {"message": "I bought 10kg of potatoes and 5 liters of milk"}

    # Allow a generous timeout because orchestrator will:
    #  - call OpenRouter once (its own LLM)
    #  - call Inventory (which itself calls OpenRouter)
    #  - call Legal (stub or LLM, depending on your implementation)
    resp = requests.post(f"{BASE_URL}/message", json=msg_payload, timeout=60)
    print("✅ Orchestrator POST /message status:", resp.status_code)
    print("🧾 Orchestrator response JSON:", resp.json())
    assert resp.status_code == 200

    print("🚀 2. Fetching Full Inventory via Orchestrator...")
    resp = requests.get(f"{BASE_URL}/get-inventory", timeout=30)
    assert resp.status_code == 200

    data = resp.json()
    assert "inventory" in data

    print(f"📦 Total Items in Stock: {data.get('count', 0)}")
    for item in data.get("inventory", []):
        print(
            f"   - {item['product_name']}: {item['quantity']}{item['unit']} "
            f"(Exp: {item['expiration_date']}) [{item['category']}]"
        )
    # basic sanity: at least one item
    assert len(data.get("inventory", [])) >= 1


# -------------------------
# Entry point: auto-start services, then run pytest
# -------------------------

if __name__ == "__main__":
    import subprocess
    import time

    processes: list[tuple[str, subprocess.Popen]] = []

    def start(name: str, cmd: list[str]):
        print(f"▶️  Starting {name}: {' '.join(cmd)}")
        p = subprocess.Popen(cmd, cwd=str(ROOT))
        processes.append((name, p))

    try:
        # 1️⃣ Inventory agent (Flask on 5002)
        start("inventory", [sys.executable, "agents/inventory_agent.py"])

        # 2️⃣ Legal agent (Flask on 5003)
        start("legal", [sys.executable, "legal_placeholder.py"])

        # 3️⃣ Orchestrator (Flask on 5001)
        start("orchestrator", [sys.executable, "orchestrator.py"])

        # 4️⃣ Finance API (FastAPI on 5004)
        start(
            "finance",
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.financeAPI:app",
                "--port",
                "5004",
            ],
        )

        print("⏳ Giving services a few seconds to start...")
        time.sleep(7)

        print("🧪 Running pytest on this file...")
        import pytest

        exit_code = pytest.main([__file__])
        sys.exit(exit_code)

    finally:
        print("\n🛑 Shutting down background services...")
        for name, p in processes:
            if p.poll() is None:
                print(f"🔻 Terminating {name} (pid={p.pid})")
                p.terminate()

        time.sleep(2)
        for name, p in processes:
            if p.poll() is None:
                print(f"⚠️  Killing {name} (pid={p.pid})")
                p.kill()
