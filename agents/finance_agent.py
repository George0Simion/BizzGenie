# agents/finance_agent.py

from typing import Dict, List
import datetime

from flask import Flask, request, jsonify

from finance_insights import collect_finance_insights
from finance_llm_client import call_llm
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.finance_db import init_db, upsert_daily_financial, add_product_financial
from db.finance_functions import get_daily_profit


app = Flask(__name__)


FINANCE_SYSTEM_PROMPT = """
You are a senior restaurant business consultant.

You receive:
- A list of detected financial insights (JSON).
- Each insight has a type, severity, time window, and evidence (numbers).

RULES:
- Do NOT invent numbers.
- Base your analysis strictly on the evidence you receive.
- First, say if action is needed (YES/NO) and how urgent.
- Explain WHY this is happening using the data (e.g. which products or costs drive changes).
- Propose 3–5 concrete, realistic actions (price changes, menu tweaks, cost optimizations).

Return JSON with fields:
- summary_markdown: short explanation for the owner (1–2 paragraphs).
- actions: list of recommended actions (short bullets).
- affected_metrics: list of metrics you are focusing on (e.g. ["profit", "revenue"]).
"""


# ---------------------------------------------------------------------------
# Core logic (unchanged)
# ---------------------------------------------------------------------------

def generate_advice_from_insights(insights: List[Dict]) -> Dict:
    if not insights:
        # nothing to say
        return {
            "summary_markdown": "I did not detect any major financial issues in the last days.",
            "actions": [],
            "affected_metrics": [],
        }

    user_message = (
        "Analyse these financial insights from the restaurant and provide "
        "explanations plus concrete actions.\n\n"
        f"INSIGHTS_JSON:\n{insights}"
    )

    llm_response = call_llm(
        system_prompt=FINANCE_SYSTEM_PROMPT,
        user_message=user_message,
        response_format="json"
    )
    return llm_response


def auto_check_and_advise(today: datetime.date | None = None) -> Dict:
    """
    Entry-point used by monitor / notification agent.
    Runs numeric detectors, then asks LLM for advice.
    """
    if today is None:
        today = datetime.date.today()

    insights = collect_finance_insights(today)
    advice = generate_advice_from_insights(insights)

    return {
        "date": today.isoformat(),
        "insights": insights,
        "advice": advice,
    }


def handle_finance_message(user_text: str,
                           today: datetime.date | None = None) -> Dict:
    """
    Entry-point used by Orchestrator for user questions like:
    'Why did profit drop last month? What should I do?'
    """
    if today is None:
        today = datetime.date.today()

    insights = collect_finance_insights(today)

    user_prompt = (
        "The restaurant owner asked: "
        f"\"{user_text}\"\n"
        "You have the following insights available.\n"
        "Answer the question explicitly, using the data.\n\n"
        f"INSIGHTS_JSON:\n{insights}"
    )

    llm_response = call_llm(
        system_prompt=FINANCE_SYSTEM_PROMPT,
        user_message=user_prompt,
        response_format="json"
    )

    return {
        "insights": insights,
        "advice": llm_response,
    }


# ---------------------------------------------------------------------------
# Helper: parse date from payload
# ---------------------------------------------------------------------------

def _get_date_from_payload(data: dict) -> datetime.date:
    ds = data.get("date")
    if ds:
        return datetime.date.fromisoformat(ds)
    return datetime.date.today()


# ---------------------------------------------------------------------------
# HTTP API
# ---------------------------------------------------------------------------

@app.route("/api/finance/auto_check", methods=["POST"])
def api_auto_check():
    """
    Body (optional):
    {
      "date": "YYYY-MM-DD"   # if omitted, uses today
    }
    """
    payload = request.get_json(silent=True) or {}
    today = _get_date_from_payload(payload)

    print(f"[finance] /auto_check for date={today}")
    result = auto_check_and_advise(today)
    return jsonify(result), 200


@app.route("/api/finance/message", methods=["POST"])
def api_finance_message():
    """
    Body:
    {
      "message": "Why did profit drop last week?",
      "date": "YYYY-MM-DD"   # optional
    }
    """
    payload = request.get_json(silent=True) or {}
    user_text = payload.get("message", "")
    today = _get_date_from_payload(payload)

    print(f"[finance] /message: {user_text} (date={today})")
    result = handle_finance_message(user_text, today)
    return jsonify(result), 200


@app.route("/api/finance/record_purchase", methods=["POST"])
def api_record_purchase():
    """
    Body:
    {
      "product_id": "chicken",
      "product_name": "Chicken breast",
      "quantity": 10,
      "unit": "kg",
      "total_cost": 1200.0,
      "date": "YYYY-MM-DD"   # optional, default today
    }

    Effect:
    - Add a product_financials row with cost = total_cost, revenue = 0.
    - Increase today's cost in daily_financials and recompute profit.
    """
    data = request.get_json(silent=True) or {}
    today = _get_date_from_payload(data)

    product_id = data.get("product_id")
    product_name = data.get("product_name") or product_id
    quantity = float(data.get("quantity") or 0.0)
    unit = data.get("unit", "")
    total_cost_raw = data.get("total_cost")

    if not product_id or total_cost_raw is None:
        return jsonify({"error": "product_id and total_cost are required"}), 400

    total_cost = float(total_cost_raw)

    print(f"[finance] /record_purchase date={today} product={product_id} "
          f"qty={quantity}{unit} cost={total_cost}")

    # 1) store per-product cost (revenue = 0)
    add_product_financial(
        date=today,
        product_id=product_id,
        product_name=product_name,
        revenue=0.0,
        cost=total_cost,
    )

    # 2) update daily cost + recompute profit
    existing = get_daily_profit(today, today)
    if existing:
        prev = existing[0]
        revenue = prev["revenue"]
        cost = prev["cost"] + total_cost
    else:
        revenue = 0.0
        cost = total_cost

    upsert_daily_financial(today, revenue=revenue, cost=cost)

    return jsonify({
        "status": "ok",
        "date": today.isoformat(),
        "product_id": product_id,
        "product_name": product_name,
        "quantity": quantity,
        "unit": unit,
        "total_cost": total_cost,
        "daily_revenue": revenue,
        "daily_cost": cost,
        "daily_profit": revenue - cost,
    }), 200


@app.route("/api/finance/set_daily_profit", methods=["POST"])
def api_set_daily_profit():
    """
    Body:
    {
      "profit": 4850.0,
      "date": "YYYY-MM-DD"   # optional, default today
    }

    Simple behaviour:
    - If a daily row exists, keep its revenue and adjust cost so that
      revenue - cost = profit.
    - Otherwise, create a row with revenue = profit, cost = 0.
    """
    data = request.get_json(silent=True) or {}
    today = _get_date_from_payload(data)

    if "profit" not in data:
        return jsonify({"error": "profit is required"}), 400

    target_profit = float(data["profit"])

    print(f"[finance] /set_daily_profit date={today} profit={target_profit}")

    existing = get_daily_profit(today, today)
    if existing:
        prev = existing[0]
        revenue = prev["revenue"]
        cost = revenue - target_profit
    else:
        revenue = target_profit
        cost = 0.0

    upsert_daily_financial(today, revenue=revenue, cost=cost)

    return jsonify({
        "status": "ok",
        "date": today.isoformat(),
        "revenue": revenue,
        "cost": cost,
        "profit": target_profit,
    }), 200


# ---------------------------------------------------------------------------
# Server start
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("[finance] Initialising DB...")
    init_db()
    print("[finance] Finance Agent running on port 5004")
    app.run(port=5004, debug=True)
