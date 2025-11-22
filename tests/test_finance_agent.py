# tests/test_finance_agent.py
import datetime
from agents import finance_agent


class DummyLLM:
    # just a helper to store the last inputs for assertions
    def __init__(self):
        self.last_system_prompt = None
        self.last_user_message = None

    def __call__(self, system_prompt, user_message, response_format="json", model=None):
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        # return a fake JSON structure similar to what the real LLM would return
        return {
            "summary_markdown": "Fake summary",
            "actions": ["Do X", "Do Y"],
            "affected_metrics": ["profit"],
        }


def test_generate_advice_from_insights_empty(monkeypatch):
    # when no insights, we MUST NOT call the LLM, and we get the default answer
    dummy = DummyLLM()
    # monkeypatch call_llm in the module
    monkeypatch.setattr(finance_agent, "call_llm", dummy)

    result = finance_agent.generate_advice_from_insights([])
    assert result["actions"] == []
    assert "Nu am detectat" in result["summary_markdown"]
    # LLM should NOT have been called
    assert dummy.last_system_prompt is None


def test_generate_advice_from_insights_nonempty(monkeypatch):
    dummy = DummyLLM()
    monkeypatch.setattr(finance_agent, "call_llm", dummy)

    fake_insights = [
        {
            "type": "overall_profit_decline",
            "severity": "high",
            "metric": "profit",
            "time_window": {"start": "2025-11-10", "end": "2025-11-19"},
            "evidence": {},
        }
    ]
    result = finance_agent.generate_advice_from_insights(fake_insights)

    # ensure we got back dummy LLM result
    assert result["summary_markdown"] == "Fake summary"
    assert result["actions"] == ["Do X", "Do Y"]
    assert "profit" in result["affected_metrics"]

    # ensure the LLM was really called and got a prompt that mentions INSIGHTS_JSON
    assert "INSIGHTS_JSON" in dummy.last_user_message