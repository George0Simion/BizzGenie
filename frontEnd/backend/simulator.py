from flask import Flask, request, jsonify
import requests
import threading
import time
import random
from datetime import datetime, timedelta

app = Flask(__name__)

PROXY_WEBHOOK_URL = "http://localhost:5000/internal/receive"

# BAZA DE DATE INITIALA (Noua structura)
inventory_db = [
    {
        "id": 1, 
        "product_name": "Tomato", 
        "category": "vegetable", 
        "quantity": 3.0, 
        "unit": "kg", 
        "min_threshold": 5.0, # Observa ca stocul e sub prag (3 < 5)
        "expiration_date": "2025-12-07",
        "auto_buy": 0
    },
    {
        "id": 2, 
        "product_name": "Potato", 
        "category": "vegetable", 
        "quantity": 15.0, 
        "unit": "kg", 
        "min_threshold": 2.0, 
        "expiration_date": "2025-12-23",
        "auto_buy": 1
    }
]

# --- WORKER INVENTAR ---
def automatic_inventory_worker():
    print("📦 [Simulator] Worker INVENTAR pornit...")
    while True:
        time.sleep(5) # Update la 5 secunde
        
        # 1. Modificăm cantitățile existentelor (simulăm consum)
        if inventory_db:
            idx = random.randint(0, len(inventory_db) - 1)
            # Scadem sau adaugam putin stoc
            change = random.choice([-0.5, 0.0, 1.0])
            inventory_db[idx]["quantity"] = max(0.0, inventory_db[idx]["quantity"] + change)

        # 2. Uneori adăugăm un produs nou
        if random.random() > 0.7:
            new_id = len(inventory_db) + 1
            products = [("Milk", "dairy", "L"), ("Eggs", "dairy", "buc"), ("Flour", "dry", "kg"), ("Basil", "herb", "buc")]
            prod = random.choice(products)
            
            # Data expirare random (intre 5 si 30 zile)
            future_date = datetime.now() + timedelta(days=random.randint(5, 30))
            
            new_item = {
                "id": new_id,
                "product_name": prod[0],
                "category": prod[1],
                "quantity": float(random.randint(1, 20)),
                "unit": prod[2],
                "min_threshold": 5.0,
                "expiration_date": future_date.strftime("%Y-%m-%d"),
                "auto_buy": random.choice([0, 1])
            }
            inventory_db.append(new_item)
            print(f"📦 [Simulator] Produs nou: {new_item['product_name']}")
        
        # 3. Trimitem formatul cerut
        # Nota: Frontend-ul se asteapta la o lista in payload.items
        payload = {
            "type": "data_update",
            "payload": {
                "category": "inventory",
                "items": list(inventory_db) 
            }
        }
        try:
            requests.post(PROXY_WEBHOOK_URL, json=payload)
        except:
            pass

# --- WORKER NOTIFICĂRI ---
def automatic_notification_worker():
    while True:
        time.sleep(20)
        # ... (Logica de notificari ramane aceeasi, nu o mai copiez ca sa fie scurt) ...
        # Poti lasa codul vechi aici

# --- LOGICA CHAT ---
def process_user_message(user_text):
    time.sleep(1)
    echo_text = f"Echo: {user_text}"
    requests.post(PROXY_WEBHOOK_URL, json={
        "type": "chat_message",
        "payload": {"text": echo_text, "sender": "ai"}
    })

@app.route('/process', methods=['POST'])
def handle_request():
    data = request.json
    user_text = (data.get('message') or data.get('msg') or "").lower()
    threading.Thread(target=process_user_message, args=(user_text,)).start()
    return jsonify({"status": "received"})

if __name__ == '__main__':
    threading.Thread(target=automatic_inventory_worker, daemon=True).start()
    # threading.Thread(target=automatic_notification_worker, daemon=True).start() # Decomenteaza daca vrei notificari
    
    print("🤖 SIMULATOR ACTUALIZAT (JSON NOU) pornit pe 5001")
    app.run(port=5001, debug=True, use_reloader=False)