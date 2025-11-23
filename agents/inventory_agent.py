import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sys

# Ensure database folder is visible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.inventory_functions import init_db, add_product, consume_product, get_alerts, get_all_inventory

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# -------------- COLOR LOGGING HELPERS --------------
def green(msg): print(f"\033[92m{msg}\033[0m")
def yellow(msg): print(f"\033[93m{msg}\033[0m")
def red(msg): print(f"\033[91m{msg}\033[0m")
def cyan(msg): print(f"\033[96m{msg}\033[0m")


# ---------------------------------------------------
# -------------- LLM QUERY FUNCTION -----------------
# ---------------------------------------------------

def query_llm(user_text):
    current_date = datetime.now().strftime("%Y-%m-%d")

    cyan(f"\n🧠 LLM REQUEST → Processing user message: '{user_text}'")

    prompt = f"""
    You are an Intelligent Inventory System. Today is {current_date}.
    User Input: "{user_text}"
    
    Tasks:
    1. Identify intent: "add" or "consume".
    2. Normalize names (e.g. "tomatoes" -> "tomato").
    3. Return JSON ONLY.
    
    Output Format:
    {{
      "action": "add" | "consume",
      "items": [
        {{ "normalized_name": "string", "quantity": number, "unit": "unit", 
           "category": "string", "auto_buy": boolean,
           "estimated_shelf_life_days": number,
           "user_specified_date": "optional YYYY-MM-DD" }}
      ]
    }}
    """

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=data
        )

        if response.status_code != 200:
            red(f"❌ LLM API Error: {response.status_code}")
            red(response.text)
            return None

        raw_content = response.json()['choices'][0]['message']['content']

        cyan("🔍 RAW LLM RESPONSE:")
        print(raw_content)

        # Strip markdown fences if present
        if "```json" in raw_content:
            raw_content = raw_content.split("```json")[1].split("```")[0]

        parsed = json.loads(raw_content.strip())

        green(f"✅ PARSED LLM JSON: {parsed}")
        return parsed

    except Exception as e:
        red(f"❌ CRITICAL ERROR talking to LLM: {e}")
        return None



# ---------------------------------------------------
# -------------- API ROUTES -------------------------
# ---------------------------------------------------

@app.route('/inventory', methods=['GET'])
def get_inventory():
    cyan("\n📦 GET /inventory called")
    try:
        inv = get_all_inventory()
        green(f"Returned {len(inv)} inventory items")
        return jsonify({"status": "success", "inventory": inv})
    except Exception as e:
        red(f"❌ Failed to fetch inventory: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/inventory/message', methods=['POST'])
def handle_message():
    cyan("\n------------------------------------------------------")
    cyan("📥 POST /inventory/message")
    cyan("------------------------------------------------------")

    data = request.json
    user_message = data.get("message", "")

    yellow(f"User message received: '{user_message}'")

    parsed = query_llm(user_message)
    if not parsed:
        red("❌ Could not parse LLM output")
        return jsonify({"error": "Parsing failed"}), 500

    action = parsed.get("action")
    items = parsed.get("items", [])

    green(f"\n📝 ACTION = {action}")
    green(f"📝 ITEMS  = {items}")

    logs = []

    # ---------------------------------------------------
    # PROCESS EACH ITEM
    # ---------------------------------------------------
    for item in items:
        name = item["normalized_name"]
        qty = float(item["quantity"])
        unit = item.get("unit", "pcs")

        cyan(f"\n🔹 Processing item:")
        print(f"      Name      = {name}")
        print(f"      Quantity  = {qty} {unit}")
        print(f"      Raw item  = {item}")

        if action == "add":
            category = item.get("category", "general")
            auto_buy = 1 if item.get("auto_buy") else 0

            # Expiration date
            if item.get("user_specified_date"):
                expiry = item["user_specified_date"]
                yellow(f"📅 Using user-specified date: {expiry}")
            else:
                days = item.get("estimated_shelf_life_days", 7)
                expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                yellow(f"📅 Using estimated shelf life: {expiry}")

            cyan("➕ ADDING PRODUCT TO DB:")
            print(f"       - name={name}")
            print(f"       - category={category}")
            print(f"       - qty={qty}")
            print(f"       - unit={unit}")
            print(f"       - expiry={expiry}")
            print(f"       - auto_buy={auto_buy}")

            result = add_product(name, category, qty, unit, expiry, auto_buy)
            green(f"   ✔ DB Result: {result}")
            logs.append(result)

        elif action == "consume":
            cyan("➖ CONSUMING PRODUCT FROM DB:")
            print(f"       - name={name}")
            print(f"       - qty={qty}")

            result = consume_product(name, qty)
            green(f"   ✔ DB Result: {result}")
            logs.append(result)



    # ---------------------------------------------------
    # CHECK ALERTS
    # ---------------------------------------------------
    cyan("\n🔔 Checking low-stock alerts...")
    alerts = get_alerts()
    yellow(f"Alerts: {alerts}")


    # ---------------------------------------------------
    # Assemble Response
    # ---------------------------------------------------
    response_text = "; ".join(logs)

    if alerts["restock_needed"]:
        response_text += "\n🛒 Auto-buy triggered for: " + ", ".join(alerts["restock_needed"])
        yellow("AUTO BUY NEEDED!")

    final = {
        "agent": "Inventory",
        "processed_data": parsed,
        "response_text": response_text,
        "alerts": alerts
    }

    green("\n📤 FINAL RESPONSE TO ORCHESTRATOR:")
    print(json.dumps(final, indent=4))

    return jsonify(final)


# ---------------------------------------------------
# SERVER START
# ---------------------------------------------------

if __name__ == '__main__':
    init_db()
    cyan("🍅 Inventory Agent running on port 5002")
    app.run(port=5002, debug=True)
