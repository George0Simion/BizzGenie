# legal.py
from comms import send_json_to_service
from flask import Flask, request, jsonify
import json

from ai_wrapper import generate_reply  # your wrapper: (system_prompt, user_prompt) -> str

app = Flask(__name__)
SERVICE_NAME = "legal"

LEGAL_SYSTEM_PROMPT = """
You are a legal assistant for a small restaurant business.

You receive:
- a "subject" describing what legal information is needed
- an optional "context" JSON with extra details

Return a short, clear explanation of:
- applicable regulations / compliance issues
- practical implications
- concrete recommendations for the owner
"""


@app.route("/input", methods=["POST"])
def handle_input():
    """
    Orchestrator calls this endpoint:

        send_json_to_service("legal", "/input", orchestrator_json)

    Expected orchestrator JSON contains a "legal" section, e.g.:

    {
        "inventory": {...},
        "legal": {
            "subject": "We want to sell alcohol after 23:00",
            "context": {
                "country": "Romania",
                "has_liquor_license": false
            }
        },
        "immediate_response": "..."
    }

    We extract the "legal" part, call the LLM, and return:

    {
        "service": "legal",
        "subject": "...",
        "context": {...},
        "analysis": "LLM-generated explanation"
    }
    """
    full_payload = request.get_json(silent=True) or {}
    print(f"[{SERVICE_NAME}] /input received full payload:", full_payload)

    legal_section = full_payload.get("legal", {})
    subject = legal_section.get("subject", "")
    context = legal_section.get("context", {})

    # Build user prompt for the LLM
    user_prompt_parts = [
        f"Subject: {subject}",
        "",
        "Context JSON:",
        json.dumps(context, indent=2, ensure_ascii=False),
    ]
    user_prompt = "\n".join(user_prompt_parts)

    # Call LLM
    analysis_text = generate_reply(
        LEGAL_SYSTEM_PROMPT,
        user_prompt
    )

    response = {
        "service": SERVICE_NAME,
        "subject": subject,
        "context": context,
        "analysis": analysis_text,
    }

    print(f"[{SERVICE_NAME}] response:", response)
    
    send_json_to_service("orchestrator", "/legal_recieve", response)
    
    
    return jsonify(response), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": SERVICE_NAME, "status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)
