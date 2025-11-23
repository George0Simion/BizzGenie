# agents/finance_llm_client.py

import os
import json
from typing import Any, Dict, Optional

import requests

# Use the same env var you already use for OpenRouter
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4.1-mini"

# Toggle verbose logging with env var; default ON
DEBUG_FINANCE_LLM = os.getenv("DEBUG_FINANCE_LLM", "1") == "1"


def _print_llm_debug_header():
    print("\n" + "=" * 80)
    print("[FINANCE LLM] call_llm() via OpenRouter")
    print("=" * 80)


def _openrouter_call(
    system_prompt: str,
    user_message: str,
    model: str,
    temperature: float = 0.2,
) -> str:
    """
    Low-level helper: send a chat completion request to OpenRouter
    and return the raw string content of the first choice.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "No OpenRouter key found. Set OPENAI_API_KEY or OPENAI_API_KEY "
            "to your sk-or-v1-... key."
        )

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        # Optional for OpenRouter analytics
        "HTTP-Referer": "http://localhost:5004",
        "X-Title": "BizzGenie Finance Agent",
    }

    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }

    print("🧠 Finance sending request to OpenRouter...")
    resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)

    if resp.status_code != 200:
        print(f"🔴 OpenRouter API Error (finance): {resp.status_code}")
        print(f"🔴 Response Body: {resp.text}")
        resp.raise_for_status()

    data = resp.json()
    content = data["choices"][0]["message"]["content"]

    return content


def call_llm(
    system_prompt: str,
    user_message: str,
    response_format: str = "json",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    High-level wrapper used by finance_agent.

    - If response_format == "json":
        we force the model to output ONLY a single JSON object,
        then json.loads() it and return the python dict.
    - Otherwise:
        we return {"text": "<raw text>"}.
    """
    if model is None:
        model = DEFAULT_MODEL

    if DEBUG_FINANCE_LLM:
        _print_llm_debug_header()
        print(f"[FINANCE LLM] model          : {model}")
        print(f"[FINANCE LLM] response_format: {response_format}")
        print("[FINANCE LLM] --- SYSTEM PROMPT (first 400 chars) ---")
        print(system_prompt[:400])
        print("[FINANCE LLM] --- USER MESSAGE (first 400 chars) ---")
        print(user_message[:400])
        if len(user_message) > 400:
            print("... (truncated)")

    if response_format == "json":
        # Strengthen the system prompt with strict JSON instructions
        strict_system_prompt = (
            system_prompt
            + "\n\nIMPORTANT:\n"
              "- RESPOND WITH A SINGLE VALID JSON OBJECT ONLY.\n"
              "- NO markdown.\n"
              "- NO ``` fences.\n"
              "- NO extra commentary.\n"
        )

        raw = _openrouter_call(
            strict_system_prompt,
            user_message,
            model=model,
            temperature=0.1,  # low temperature for more deterministic JSON
        )

        if DEBUG_FINANCE_LLM:
            print("[FINANCE LLM] --- RAW JSON TEXT (from OpenRouter) ---")
            print(raw)
            print("[FINANCE LLM] ---------------------------------------")

        # In case the model still wraps in ```json ``` or ``` ```
        if "```" in raw:
            # try to peel off any code fences
            parts = raw.split("```json")
            if len(parts) > 1:
                raw = parts[1]
            else:
                parts = raw.split("```")
                if len(parts) > 1:
                    raw = parts[1]
            raw = raw.split("```")[0]

        raw = raw.strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            print("[FINANCE LLM] !!! JSON DECODE ERROR !!!")
            print(f"Error: {e}")
            print("Offending text:")
            print(raw)
            raise

        return parsed

    else:
        # Plain text mode – e.g. if you ever want a natural-language answer
        raw = _openrouter_call(
            system_prompt,
            user_message,
            model=model,
            temperature=0.7,
        )

        if DEBUG_FINANCE_LLM:
            print("[FINANCE LLM] --- RAW TEXT RESPONSE (from OpenRouter) ---")
            print(raw)
            print("[FINANCE LLM] -----------------------------------------")

        return {"text": raw}
