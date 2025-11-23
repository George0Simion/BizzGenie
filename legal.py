# legal.py
from comms import send_json_to_service
from flask import Flask, request, jsonify
import json
import threading

from ai_wrapper import generate_reply  # your wrapper: (system_prompt, user_prompt) -> str

app = Flask(__name__)
SERVICE_NAME = "legal"
DEEP_RESEARCH_MODEL = "openai/gpt-4.1"
LEGAL_DEBUG_PATH = "legal_latest.json"

TRUSTED_SOURCES = [
    "legislatie.just.ro",
]

LEGAL_SYSTEM_PROMPT = """
You are a legal research analyst for a small restaurant business.
Perform web-style deep research and return only JSON, no prose.
Always prefer primary sources and official sites. If a citation is not from a trusted/legal government or institutional source, state that it needs verification and set source to "needs-verification".
Use only sources from the provided trusted list when possible; otherwise mark as "needs-verification".
RESPONSE FORMAT RULES (must follow):
- Return a single JSON object only. No markdown, no code fences, no extra text.
- Each checklist item must include: step, action, citation (law/reg/article), source (URL).
- Each risk item must include: risk, mitigation, citation (law/reg/article), source (URL).
- summary must be 2-4 sentences and include inline bracketed citations like [citation reference].
- Keep checklist concise (max 5 steps) and risks concise (max 3 items). Be brief to avoid truncation.
The JSON must contain:
- service: "legal"
- subject: the subject you received
- context: echo the provided context
- research: {
    "summary": 2-4 sentence summary with citations inline,
    "checklist": [
       {
         "step": short imperative,
         "action": what to do,
         "citation": specific law/regulation/article,
         "source": URL to the cited document
       }
    ],
    "risks": [
       {
         "risk": concise risk,
         "mitigation": action to reduce risk,
         "citation": law/reg guidance,
         "source": URL
       }
    ]
  }
Rules:
- Cite concrete provisions (law name/number, article/section). Include a working URL for each citation.
- If uncertain, mark citation as "Unknown - verify locally" and source "needs-verification".
- Keep JSON valid; no markdown, no code fences.
"""

# In-memory storage for the latest research artifact
LATEST_RESEARCH_RESULT = None


def _build_user_prompt(subject: str, context: dict) -> str:
    return "\n".join([
        f"Subject: {subject}",
        "",
        "Context JSON:",
        json.dumps(context or {}, indent=2, ensure_ascii=False),
        "",
        "Trusted source domains (prefer these; otherwise mark as needs-verification):",
        ", ".join(TRUSTED_SOURCES),
        "",
        "Checklist: max 5 steps. Risks: max 3 items. Be concise.",
        "",
        "Produce the JSON as specified. Do not wrap in Markdown.",
    ])


def _strip_markdown_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped[stripped.find("\n") + 1 :]
        if stripped.rfind("```") != -1:
            stripped = stripped[: stripped.rfind("```")]
    return stripped.strip()


def _extract_braced_block(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            return text
    return text


def _parse_or_fallback(raw_text: str, subject: str, context: dict) -> dict:
    cleaned = _strip_markdown_fences(raw_text)
    cleaned = _extract_braced_block(cleaned)
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        if isinstance(parsed, dict):
            parsed.setdefault("service", SERVICE_NAME)
            parsed.setdefault("subject", subject)
            parsed.setdefault("context", context)
            parsed.setdefault("research", {}).setdefault("checklist", [])
            parsed["research"].setdefault("risks", [])
            parsed["research"].setdefault("summary", "")
        return parsed
    except Exception:
        return {
            "service": SERVICE_NAME,
            "subject": subject,
            "context": context,
            "research": {
                "summary": "Model response was not valid JSON. See raw_response.",
                "checklist": [],
                "risks": []
            },
            "raw_response": raw_text
        }


def _persist_latest_result(payload: dict):
    try:
        with open(LEGAL_DEBUG_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"[{SERVICE_NAME}] Latest research persisted to {LEGAL_DEBUG_PATH}")
    except Exception as e:
        print(f"[{SERVICE_NAME}] Failed to persist debug JSON: {e}")


def _run_research(subject: str, context: dict):
    global LATEST_RESEARCH_RESULT
    try:
        user_prompt = _build_user_prompt(subject, context)
        research_text = generate_reply(
            LEGAL_SYSTEM_PROMPT,
            user_prompt,
            model=DEEP_RESEARCH_MODEL,
            temperature=0.3,
            max_tokens=1500
        )
        parsed = _parse_or_fallback(research_text, subject, context)
        LATEST_RESEARCH_RESULT = parsed
        print(f"[{SERVICE_NAME}] Parsed research JSON:\n{json.dumps(parsed, ensure_ascii=False, indent=2)}")
        _persist_latest_result(parsed)
        send_json_to_service("orchestrator", "/legal_recieve", parsed)
    except Exception as e:
        print(f"[{SERVICE_NAME}] Deep research error: {e}")
        error_payload = {
            "service": SERVICE_NAME,
            "subject": subject,
            "context": context,
            "error": str(e)
        }
        LATEST_RESEARCH_RESULT = error_payload
        _persist_latest_result(error_payload)
        send_json_to_service("orchestrator", "/legal_recieve", error_payload)


@app.route("/input", methods=["POST"])
def handle_input():
    full_payload = request.get_json(silent=True) or {}
    print(f"[{SERVICE_NAME}] /input received full payload:", full_payload)

    legal_section = full_payload.get("legal", {})
    subject = legal_section.get("subject", "")
    context = legal_section.get("context", {})

    t = threading.Thread(target=_run_research, args=(subject, context), daemon=True)
    t.start()

    ack = {
        "service": SERVICE_NAME,
        "subject": subject,
        "context": context,
        "status": "research_started"
    }

    print(f"[{SERVICE_NAME}] research job dispatched.")
    return jsonify(ack), 202


@app.route("/latest", methods=["GET"])
def latest():
    if LATEST_RESEARCH_RESULT is None:
        return jsonify({"service": SERVICE_NAME, "status": "no_result"}), 404
    return jsonify(LATEST_RESEARCH_RESULT), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": SERVICE_NAME, "status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)
