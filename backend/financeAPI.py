from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# Import your finance agent
from agents.finance_agent import auto_check_and_advise, handle_finance_message

app = FastAPI(title="BizzGenie Backend")

# ---------- Request/response models ----------

class FinanceMessageRequest(BaseModel):
    message: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/finance/auto_check")
def api_finance_auto_check():
    """
    Called by monitor / Notification Agent or manually from UI.
    No input needed; just runs detectors and LLM advice.
    """
    result = auto_check_and_advise()
    # result is already dict with date, insights, advice
    return result


@app.post("/api/finance/message")
def api_finance_message(body: FinanceMessageRequest):
    """
    Called when the user asks a finance/business question in the chat:
    e.g. "De ce a scăzut profitul luna trecută?"
    """
    result = handle_finance_message(user_text=body.message)
    return result
