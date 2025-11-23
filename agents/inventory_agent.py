import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
# Import DB functions from the file above
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.inventory_functions import init_db, add_product, consume_product, get_alerts

app = Flask(__name__)

# 🔑 CONFIGURATION

site_url = "http://localhost:5000"
app_name = "InventoryAgent"

# Initialize DB on startup
init_db()

def query_llm(user_text):
    """
    Uses LLM to parse natural language into Structured JSON for the DB.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    You are an Inventory Manager API.
    Today's date is: {current_date}.
    
    User input: "{user_text}"
    
    Extract the following information and return ONLY valid JSON (no markdown):
    1. action: "add" or "consume" or "query"
    2. items: a list of objects {{ "name": "string", "quantity": number, "unit": "kg/pcs/l", "expiration_date": "YYYY-MM-DD" (only for add, default to today + 7 days if missing) }}
    
    Example JSON output:
    {{
      "action": "add",
      "items": [
        {{ "name": "tomatoes", "quantity": 5, "unit": "kg", "expiration_date": "2024-12-01" }}
      ]
    }}
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/gpt-3.5-turbo", # Or any model available on OpenRouter
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response_json = response.json()
        content = response_json['choices'][0]['message']['content']
        # Clean up potential markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        return json.loads(content.strip())
    except Exception as e:
        print(f"LLM Error: {e}")
        return None

@app.route('/inventory/message', methods=['POST'])
def handle_message():
    """
    Endpoint called by the Orchestrator.
    Input JSON expected: { "message": "I bought 10 eggs expiring next friday" }
    """
    data = request.json
    user_message = data.get('message', '')

    # 1. AI Processing -> Parse Intent
    parsed_data = query_llm(user_message)
    
    if not parsed_data:
        return jsonify({"error": "Failed to parse message"}), 500

    action = parsed_data.get('action')
    items = parsed_data.get('items', [])
    execution_logs = []

    # 2. Database Execution
    for item in items:
        name = item['name'].lower()
        qty = float(item['quantity'])
        unit = item.get('unit', 'pcs')
        
        if action == "add":
            expiry = item.get('expiration_date')
            result = add_product(name, qty, unit, expiry)
            execution_logs.append(result)
            
        elif action == "consume":
            result = consume_product(name, qty)
            execution_logs.append(result)

    # 3. Intelligent Checks (Decision Making)
    # After the action, we check the health of the inventory
    alerts = get_alerts()
    
    response_text = f"Action Processed: {'; '.join(execution_logs)}."
    
    # Append critical alerts to the response
    if alerts['expired']:
        response_text += f"\n⚠️ DISCARD: {', '.join(alerts['expired'])}"
    
    if alerts['restock_needed']:
        response_text += f"\n🛒 BUY LIST: {', '.join(alerts['restock_needed'])}"
    
    if alerts['expiring_soon']:
        response_text += f"\n⏳ USE SOON: {', '.join(alerts['expiring_soon'])}"

    # Return JSON to Orchestrator
    return jsonify({
        "agent": "Inventory",
        "processed_data": parsed_data,
        "response_text": response_text,
        "alerts_payload": alerts # Automation agent can use this raw data
    })

if __name__ == '__main__':
    print("🍅 Inventory Agent running on port 5002")
    app.run(port=5002, debug=True)
