# ai_wrapper.py
import os
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4.1-mini"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 256

# Read env var once at import
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def generate_reply(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
):
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY not set or empty. "
            "Export it before running: export OPENAI_API_KEY='sk-or-v1-...'"
        )

    # DEBUG: show that we have a key and model
    print("[DEBUG] Using model:", model)
    print("[DEBUG] OPENAI_API_KEY starts with:", OPENAI_API_KEY[:10])

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        # Optional:
        "HTTP-Referer": "http://localhost",
        "X-Title": "Simple Test Script",
    }

    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    resp = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=60)

    # Extra debug if not 2xx
    if not resp.ok:
        print("[DEBUG] Status code:", resp.status_code)
        print("[DEBUG] Response body:", resp.text)
        resp.raise_for_status()

    data = resp.json()
    return data["choices"][0]["message"]["content"]