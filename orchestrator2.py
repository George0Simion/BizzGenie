from flask import Flask, request, jsonify
from threading import Thread
from comms import send_json_to_service, SERVICE_URLS
import time
from ai_wrapper import generate_reply
import requests
import json
import requests

app = Flask(__name__)

LANGUAGE = "ROMANIAN"
previous_answererd = True

USER_RESPONSE_STACK = []

SERVICE_NAME = "orchestrator"
SYSTEM_PROMT_USER = """
You are an AI agents manager called Orchestrator. You will receive messages from a small bussiness owner user and commmand the other AI services (legal, predictor , invetory , notification agent)
to get their input.

    The user is running a small restaurant business.    

    The bussiness owner will tell you what they did and you must decide what actions to take.
    
    The bussinser owner is not experienced in managing a bussiness so you must think of all the implications of their actions and command the agents accordingly.

    AGENTS YOU CAN COMMAND:
    1. legal: This agent returns legal information about compliance, regulations, and policies given the subject.
    2. inventory: This agent keeps track of stock levels, adds or removes items from inventory based on user actions.
    3. finance: This agent analyzes financial data (profit trends, product drivers, etc.) and returns advice and insights.
       - Use it when the user asks about profit, revenue, costs, or "what should I do with my business finance".
       - You can either:
         - run an automatic check (no specific question), or
         - ask a concrete finance question.

    YOUR TASK:
        The user will send simple messages you must interpret them and expand on the request to command the agents.
        The user might not think of all implications so you must think of what agents to command to fulfill the user request.
    
    You must format the response as a JSON object with one of the following structures:

    1. If you know what actions to take, respond with something like:

    {
        "inventory": [
            {
                "action": "add stock" / "remove stock",
                "details": {
                    "item_id": "string identifying the item's name",
                    "quantity": 10,
                    "quantity_unit": "kg"
                }
            }
        ],
        "legal": {
            "subject": "string describing what legal information is needed"
        },
        "finance": {
            "mode": "auto_check" 
        },
        "immediate_response": "string with a message acknowledging the user request and summarizing the actions taken"
    }
    
    2. If you need more information from the user to decide what actions to take, respond with:
    {
        "question": "string with a message asking the user for more information"
    }
"""
SYSTEM_PROMT_USER = SYSTEM_PROMT_USER + f"all responses must be in {LANGUAGE} language."
SYSTEM_PROMT_INTERNAL = ""


def list_to_string(lst, sep="\n"):
    return sep.join(str(x) for x in lst)


def parse_main_request_data(text: str):
    """
    Procesează mesajul utilizatorului, apelează modelul și:
      - trimite comenzi către agenții (legal, inventory etc.)
      - trimite un răspuns scurt către proxy prin send_chatbox_response_to_proxy(text)
    """
    global USER_RESPONSE_STACK

    # Build history string
    previous_messages = list_to_string(USER_RESPONSE_STACK)
    print("previous messages:", previous_messages)

    # Add current user message to stack
    USER_RESPONSE_STACK.append(text)

    # Build user prompt
    user_prompt = previous_messages + "\nUSER: " + text if previous_messages else text

    # Call the model
    raw_response = generate_reply(
        SYSTEM_PROMT_USER,
        user_prompt
    )
    print("orchestrator raw response:", raw_response)

    # Parse JSON
    try:
        response = json.loads(raw_response)
    except json.JSONDecodeError:
        print("WARNING: Orchestrator returned non-JSON. Using raw text as immediate_response.")
        response = {"immediate_response": raw_response}

    print("orchestrator parsed response:", response)

    text_for_user = None

    # CASE 2: ACTIONS
    # --- INVENTORY CALL ---
    if "inventory" in response:
        inv_block = response["inventory"]

        # Allow both single-object and list-of-objects formats
        if isinstance(inv_block, dict):
            inv_list = [inv_block]
        else:
            inv_list = list(inv_block)

        inventory_results = []

        for inv in inv_list:
            details = inv.get("details", {})
            item = details.get("item_id")
            qty = details.get("quantity")
            unit = details.get("quantity_unit", "")
            action = inv.get("action", "")

            # skip malformed entries
            if not item or qty is None:
                continue

            if "add" in action:
                inv_text = f"I bought {qty}{unit} of {item}"
            else:
                inv_text = f"I used {qty}{unit} of {item}"

            inv_result = send_json_to_service(
                "inventory",
                "/inventory/message",
                {"message": inv_text}
            )
            inventory_results.append(inv_result)

        response["inventory_result"] = inventory_results


    # --- LEGAL CALL ---
        # --- LEGAL CALL ---
    if "legal" in response:
        leg = response["legal"]
        legal_result = send_json_to_service(
            "legal",
            "/send",
            {"subject": leg.get("subject", "general inquiry")}
        )
        response["legal_result"] = legal_result

    # --- FINANCE CALL ---
    if "finance" in response:
        fin_block = response["finance"]
        mode = fin_block.get("mode", "auto_check")
        print("[orchestrator] Finance block received:", fin_block)

        if mode == "auto_check":
            # no extra payload
            finance_result = send_json_to_service(
                "finance",
                "/api/finance/auto_check",
                {}
            )
        elif mode == "message":
            question = fin_block.get("question", "")
            finance_result = send_json_to_service(
                "finance",
                "/api/finance/message",
                {"message": question}
            )
        else:
            finance_result = {"error": f"Unknown finance mode '{mode}'"}

        response["finance_result"] = finance_result


    # After full resolution, clear context
    print("Conversation for this request resolved, clearing USER_RESPONSE_STACK")
    USER_RESPONSE_STACK.clear()

    return response


@app.route("/text", methods=["POST"])
def handle_text():
    data = request.get_json(silent=True) or {}
    message = data.get("msg", "")  # old client uses {"msg": "..."}
    print("Processing /text message:", message)

    result = parse_main_request_data(message)
    return jsonify(result), 200

@app.route("/message", methods=["POST"])
def handle_message():
    """
    For your newer test script that sends {"message": "..."}
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    print("Processing /message:", message)

    result = parse_main_request_data(message)
    return jsonify(result), 200


@app.route("/legal", methods=["POST"])
def receive_legal():
    """
    Endpoint for legal service to call back.
    """
    data = request.get_json(silent=True) or {}
    print("[orchestrator] /legal callback:", data)
    return jsonify({"status": "ok"}), 200

import requests   # <-- add this





@app.route("/get-inventory", methods=["GET"])
def proxy_get_inventory():
    """
    Simple proxy to Inventory /inventory GET
    """
    base = SERVICE_URLS.get("inventory")
    url = base + "/inventory"
    print(f"[orchestrator] Proxying GET to inventory: {url}")

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        inv_data = resp.json()
        return jsonify(inv_data), 200
    except Exception as e:
        print("[orchestrator] Error fetching inventory:", e)
        return jsonify({"error": str(e)}), 500





if __name__ == "__main__":
    app.run(port=5001, debug=True)
