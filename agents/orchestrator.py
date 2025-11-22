import sys
import os
import json
from flask import Flask, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.ai_wrapper import generate_reply
from utils.comms import send_json_to_service

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are the Orchestrator. 
User Input: Business owner request.
Output: JSON routing plan.

AGENTS:
1. inventory: Handles stock.
2. legal: Handles regulations.

Format:
{
    "inventory": { "should_call": true, "instruction": "Add 3kg tomatoes" },
    "legal": { "should_call": true, "subject": "Storage of fresh vegetables" },
    "immediate_response": "I have started the process..."
}
"""

@app.route("/message", methods=["POST"])
def handle_message():
    user_text = request.json.get("message", "")
    print(f"🎼 Orchestrator received: {user_text}")

    # 1. Ask LLM for the plan
    raw_plan = generate_reply(SYSTEM_PROMPT, user_text)
    
    # Clean JSON string
    if "```json" in raw_plan:
        raw_plan = raw_plan.split("```json")[1].split("```")[0]
    
    try:
        plan = json.loads(raw_plan)
    except:
        return jsonify({"error": "Orchestrator failed to parse plan"}), 500

    results = {}

    # 2. Execute Inventory Call if needed
    if plan.get("inventory", {}).get("should_call"):
        # Inventory Agent expects {"message": "..."}
        inv_payload = {"message": plan["inventory"]["instruction"]}
        # Note the path matches what is inside inventory_agent.py
        inv_resp = send_json_to_service("inventory", "/inventory/message", inv_payload)
        results["inventory"] = inv_resp

    # 3. Execute Legal Call if needed
    if plan.get("legal", {}).get("should_call"):
        legal_payload = {"subject": plan["legal"]["subject"]}
        legal_resp = send_json_to_service("legal", "/send", legal_payload)
        results["legal"] = legal_resp

    # 4. Compile Final Response
    final_response = {
        "user_message": user_text,
        "orchestrator_plan": plan,
        "agent_results": results,
        "summary": plan.get("immediate_response")
    }

    return jsonify(final_response)

if __name__ == "__main__":
    print("🎼 Orchestrator running on port 5001")
    app.run(port=5001, debug=True)