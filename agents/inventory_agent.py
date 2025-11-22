import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.inventory_functions import init_db, add_product, consume_product, get_alerts

app = Flask(__name__)

# 🔑 CONFIGURATION
# init_db() # Run this once to create the file, then comment out if you want

def query_llm(user_text):
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # 🧠 SMART PROMPT
    prompt = f"""
    You are an Intelligent Inventory System. Today is {current_date}.
    User Input: "{user_text}"

    Tasks:
    1. Identify intent: "add" or "consume".
    2. NORMALIZE NAMES: Convert variations like "ciresi", "ciresica" to standard singular "cirese". "Tomatoes" -> "tomato".
    3. CATEGORIZE: Assign a category (e.g., Dairy, Fruit, Vegetable, Meat, Pantry).
    4. AUTO-BUY: Should this be automatically restocked? (True for essentials like milk/bread, False for treats).
    5. EXPIRATION: If user does NOT specify a date, estimate a HARDCODED shelf life in DAYS from today based on the item type (e.g., Milk=7, Rice=365).

    Return JSON ONLY:
    {{
      "action": "add" | "consume",
      "items": [
        {{
          "normalized_name": "string (lowercase)",
          "original_name": "string",
          "quantity": number,
          "unit": "kg/pcs/l",
          "category": "string",
          "auto_buy": boolean,
          "estimated_shelf_life_days": number (integer),
          "user_specified_date": "YYYY-MM-DD" (or null if not mentioned)
        }}
      ]
    }}
    """

    headers = {
        "Authorization": f"Bearer {OPEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/gpt-4o-mini", # Or any robust model
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        content = response.json()['choices'][0]['message']['content']
        # Clean markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        return json.loads(content.strip())
    except Exception as e:
        print(f"LLM Error: {e}")
        return None

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
    app.run(port=5002, debug=True)