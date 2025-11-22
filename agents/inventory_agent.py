import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sys

# Ensure we can find the db folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.inventory_functions import init_db, add_product, consume_product, get_alerts, get_all_inventory

app = Flask(__name__)

# 🔑 CONFIGURATION
# HARDCODE YOUR KEY HERE FOR TESTING
OPENROUTER_API_KEY = "sk-or-v1-..." 

def query_llm(user_text):
    current_date = datetime.now().strftime("%Y-%m-%d")
    
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
        {{ "normalized_name": "string", "quantity": number, "unit": "unit", "category": "string", "auto_buy": boolean, "estimated_shelf_life_days": number, "user_specified_date": "YYYY-MM-DD (optional)" }}
      ]
    }}
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5002"
    }
    
    data = {
        "model": "openai/gpt-4o-mini", 
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        print(f"🧠 Inventory sending request to OpenRouter...")
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code != 200:
            print(f"🔴 OpenRouter API Error: {response.status_code}")
            print(f"🔴 Response Body: {response.text}")
            return None

        content = response.json()['choices'][0]['message']['content']
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
            
        return json.loads(content.strip())
        
    except Exception as e:
        print(f"🔴 CRITICAL LLM EXCEPTION: {e}")
        return None

# --- NEW GET ENDPOINT ---
@app.route('/inventory', methods=['GET'])
def get_inventory():
    """
    Returns the full inventory state as JSON.
    Useful for the frontend dashboard.
    """
    data = get_all_inventory()
    return jsonify({
        "status": "success",
        "count": len(data),
        "inventory": data
    })

@app.route('/inventory/message', methods=['POST'])
def handle_message():
    data = request.json
    user_message = data.get('message', '')

    parsed_data = query_llm(user_message)
    
    if not parsed_data:
        return jsonify({"error": "Failed to parse"}), 500

    action = parsed_data.get('action')
    items = parsed_data.get('items', [])
    logs = []

    for item in items:
        # Use the Normalized Name for DB consistency
        name = item['normalized_name']
        qty = float(item['quantity'])
        unit = item.get('unit', 'pcs')
        
        if action == "add":
            category = item.get('category', 'general')
            auto_buy = 1 if item.get('auto_buy') else 0
            
            # Date Logic: User specified OR Calculated Hardcoded
            if item.get('user_specified_date'):
                expiry = item['user_specified_date']
            else:
                # Calculate expiry based on LLM's shelf life estimate
                days_to_add = item.get('estimated_shelf_life_days', 7)
                expiry = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")

            result = add_product(name, category, qty, unit, expiry, auto_buy)
            logs.append(result)
            
        elif action == "consume":
            result = consume_product(name, qty)
            logs.append(result)

    alerts = get_alerts()
    
    response_text = f"✅ {'; '.join(logs)}."
    
    if alerts['restock_needed']:
        response_text += f"\n🛒 AUTO-BUY NEEDED: {', '.join(alerts['restock_needed'])}"
    
    return jsonify({
        "agent": "Inventory",
        "processed_data": parsed_data,
        "response_text": response_text,
        "alerts": alerts
    })

if __name__ == '__main__':
    # Initialize DB if it doesn't exist
    init_db()
    print("🍅 Inventory Agent running on port 5002")
    app.run(port=5002, debug=True)