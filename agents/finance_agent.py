# /agents/finance_agent.py
from typing import Dict, List
import datetime
from .finance_insights import collect_finance_insights
from .finance_llm_client import call_llm

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
- Propose 3-5 concrete, realistic actions (price changes, menu tweaks, cost optimizations).

Return JSON with fields:
- summary_markdown: short explanation for the owner (1-2 paragraphs).
- actions: list of recommended actions (short bullets).
- affected_metrics: list of metrics you are focusing on (e.g. ["profit", "revenue"]).
"""

def generate_advice_from_insights(insights: List[Dict]) -> Dict:
    if not insights:
        # nothing to say
        return {
            "summary_markdown": " Nu am detectat probleme financiare majore în ultimele zile.",
            "actions": [],
            "affected_metrics": [],
        }

    user_message = (
        "Analizează aceste insight-uri financiare din restaurant și oferă explicații + acțiuni.\n\n"
        f"INSIGHTS_JSON:\n{insights}"
    )

    llm_response = call_llm(
        system_prompt=FINANCE_SYSTEM_PROMPT,
        user_message=user_message,
        response_format="json"  # if your client supports this
    )
    # llm_response should already be a dict; if it's text, json.loads().
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
    'De ce a scăzut profitul luna trecută? Ce să fac?'
    - Reuse the same insight engine.
    - Optionally include the original question in the prompt.
    """
    if today is None:
        today = datetime.date.today()

    insights = collect_finance_insights(today)

    user_prompt = (
        "Proprietarul a întrebat: "
        f"\"{user_text}\"\n"
        "Ai la dispoziție insight-urile de mai jos.\n"
        "Răspunde explicit la întrebare, folosindu-te de date.\n\n"
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
