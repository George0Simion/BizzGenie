from flask import Flask, request, jsonify
from threading import Thread
from comms import send_json_to_service, SERVICE_URLS
import time
from ai_wrapper import generate_reply
import json
import requests

app = Flask(__name__)

LANGUAGE = "ROMANIAN"
previous_answererd = True

USER_RESPONSE_STACK = []

SERVICE_NAME = "orchestrator"

# --- Proxy config ---
PROXY_BASE_URL = "http://localhost:5000"
PROXY_ORCHESTRATOR_ROUTE = "/from_orchestrator"


def dispatch_to_service_async(service_name: str, endpoint: str, payload: dict):
    """
    Trimite payload-ul către un serviciu în fundal (fire-and-forget),
    fără să blocheze orchestratorul.
    """
    def _worker():
        try:
            print(f"[orchestrator] Async send to service={service_name}, endpoint={endpoint}")
            send_json_to_service(service_name, endpoint, payload)
            print(f"[orchestrator] Async send to {service_name}{endpoint} DONE")
        except Exception as e:
            print(f"[orchestrator] ERROR sending to {service_name}{endpoint}: {e}")

    t = Thread(target=_worker, daemon=True)
    t.start()


def send_chatbox_response_to_proxy(text: str):
    """
    Trimite răspunsul rapid al orchestratorului direct către proxy.
    Proxy-ul îl va trimite în chatbox imediat.
    Format:
        {
            "type": "chatbox_response",
            "text": "<text>"
        }
    """
    payload = {
        "type": "chatbox_response",
        "text": text
    }
    try:
        url = f"{PROXY_BASE_URL}{PROXY_ORCHESTRATOR_ROUTE}"
        print(f"[orchestrator] Sending chatbox_response to proxy: {payload}")
        resp = requests.post(url, json=payload, timeout=5)
        print(f"[orchestrator] Proxy responded with status {resp.status_code}")
    except Exception as e:
        print(f"[orchestrator] Failed to send chatbox_response to proxy: {e}")


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
      - trimite comenzi către agenții (legal, inventory, finance etc.) asincron
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

    # CASE 1: MODEL ASKS A QUESTION → keep context, do NOT clear stack
    if "question" in response:
        question = response["question"]
        USER_RESPONSE_STACK.append(question)
        print("orchestrator question to user:", question)
        text_for_user = question

    else:
        # CASE 2: ACTIONS (INVENTORY / LEGAL / FINANCE) + IMMEDIATE RESPONSE

        # --- INVENTORY CALL (merged, async) ---
        if "inventory" in response:
            inv_block = response["inventory"]

            # Allow both single-object and list-of-objects formats
            if isinstance(inv_block, dict):
                inv_list = [inv_block]
            else:
                inv_list = list(inv_block)

            for inv in inv_list:
                details = inv.get("details", {})
                item = details.get("item_id")
                qty = details.get("quantity")
                unit = details.get("quantity_unit", "")
                action = inv.get("action", "")

                # skip malformed entries
                if not item or qty is None:
                    continue

                # You can localize this text if you want
                if "add" in action:
                    inv_text = f"I bought {qty}{unit} of {item}"
                else:
                    inv_text = f"I used {qty}{unit} of {item}"

                # fire-and-forget towards inventory service
                dispatch_to_service_async(
                    "inventory",
                    "/inventory/message",
                    {"message": inv_text}
                )

        # --- LEGAL CALL (keep current behaviour) ---
        if "legal" in response:
            leg = response["legal"]
            # here you keep the old contract; adjust if needed
            dispatch_to_service_async("legal", "/input", response)

        # --- FINANCE CALL (merged, async) ---
        if "finance" in response:
            fin_block = response["finance"]
            mode = fin_block.get("mode", "auto_check")
            print("[orchestrator] Finance block received:", fin_block)

            if mode == "auto_check":
                dispatch_to_service_async(
                    "finance",
                    "/api/finance/auto_check",
                    {}
                )
            elif mode == "message":
                question = fin_block.get("question", "")
                dispatch_to_service_async(
                    "finance",
                    "/api/finance/message",
                    {"message": question}
                )
            else:
                print(f"[orchestrator] Unknown finance mode '{mode}'")

        # --- TEXT FOR USER ---
        if "immediate_response" in response:
            print("orchestrator immediate response:", response["immediate_response"])
            text_for_user = response["immediate_response"]

        if not text_for_user:
            text_for_user = "Am procesat cererea ta."

        # Now that everything is resolved for this “thread”, clear context
        print("Conversation for this request resolved, clearing USER_RESPONSE_STACK")
        USER_RESPONSE_STACK.clear()

    # Send the quick chatbox response to proxy
    send_chatbox_response_to_proxy(text_for_user)

    return response


@app.route("/text", methods=["POST"])
def handle_text():
    """
    PRIMEȘTE JSON de la proxy.
    Nu întoarce date reale pentru UI.
    Tot ce este vizibil pentru user se trimite înapoi la proxy
    prin send_chatbox_response_to_proxy().
    """
    try:
        data = request.get_json(silent=False) or {}
    except Exception as e:
        print("Error parsing JSON from proxy:", e)
        return jsonify({"error": "Invalid JSON"}), 400

    print("Received JSON from proxy on /text:", data)

    message = data.get("msg") or data.get("text") or ""
    context = data.get("context", {}) or {}

    print("Processing message:", message)
    print("Context:", context)

    # Trigger the logic; it will call send_chatbox_response_to_proxy() internally
    parse_main_request_data(message)

    # Minimal ACK; proxy ignores this content
    return "", 204


def send_message(data):
    send_json_to_service("frontend", "/send_message", data)


@app.route("/legal_recieve", methods=["POST"])
def legal_recieve():
    data = request.json or {}
    print("Received legal data:", data)
    research = data.get("research", {})

    payload = {
        "type": "data_update",
        "payload": {
            "category": "legal_research",
            "subject": data.get("subject"),
            "summary": research.get("summary", ""),
            "checklist": research.get("checklist", []),
            "risks": research.get("risks", []),
            "context": data.get("context", {}),
            "source_service": "legal"
        }
    }

    # forward structured update to proxy
    try:
        url = f"{PROXY_BASE_URL}{PROXY_ORCHESTRATOR_ROUTE}"
        print(f"[orchestrator] Forwarding legal update to proxy: {payload}")
        resp = requests.post(url, json=payload, timeout=5)
        print(f"[orchestrator] Proxy responded with status {resp.status_code}")
    except Exception as e:
        print(f"[orchestrator] Failed to forward legal update to proxy: {e}")

    # optional chat surface
    if research.get("summary"):
        chat_text = f"[Legal] {research.get('summary')}"
        send_chatbox_response_to_proxy(chat_text)

    return jsonify({"status": "received", "data": data}), 200


@app.route("/receive_inventory", methods=["GET"])
def receive_inventory():
    # receive inventory data from inventory service (if used as callback)
    data = request.json
    print("Received inventory data:", data)
    return jsonify({"status": "received", "data": data}), 200


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
