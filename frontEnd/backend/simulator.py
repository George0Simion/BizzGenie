from flask import Flask, request, jsonify
import requests
import threading
import time
import random
from datetime import datetime, timedelta

app = Flask(__name__)

PROXY_WEBHOOK_URL = "http://localhost:5000/internal/receive"

# DATE
inventory_db = [
    {"id": 1, "product_name": "Tomato", "category": "vegetable", "quantity": 3.0, "unit": "kg", "min_threshold": 5.0, "expiration_date": "2025-12-07", "auto_buy": 0},
    {"id": 2, "product_name": "Potato", "category": "vegetable", "quantity": 15.0, "unit": "kg", "min_threshold": 2.0, "expiration_date": "2025-12-23", "auto_buy": 1}
]

legal_db = [
    {"id": 101, "title": "Înregistrare ONRC", "status": "completed", "description": "Procesul obligatoriu.", "steps": [{"step": "Rezervare nume", "done": True}, {"step": "Depunere dosar", "done": True}]},
    {"id": 102, "title": "Autorizație Funcționare", "status": "in_progress", "description": "Acord primărie.", "steps": [{"step": "Contract Salubritate", "done": True}, {"step": "Depunere cerere", "done": False}]}
]

# --- RUTE ---
@app.route('/process', methods=['POST'])
def handle_request():
    data = request.json
    user_text = data.get('message') or data.get('msg') or ""
    print(f"📩 [Simulator] Chat: '{user_text}'")
    threading.Thread(target=process_user_message, args=(user_text,)).start()
    return jsonify({"status": "received"})

@app.route('/legal/save', methods=['POST'])
def handle_legal_save():
    global legal_db
    data = request.json
    if 'tasks' in data:
        print("💾 [Simulator] Update Legal primit.")
        legal_db = data['tasks']
        def send_confirm():
            time.sleep(1)
            try:
                requests.post(PROXY_WEBHOOK_URL, json={
                    "type": "notification",
                    "payload": {"title": "Modificări Salvate", "desc": "Datele legale au fost actualizate.", "type": "info"}
                })
            except: pass
        threading.Thread(target=send_confirm).start()
    return jsonify({"status": "saved"})

# --- LOGICA ---
def process_user_message(user_text):
    time.sleep(1) 
    echo_text = f"Echo: {user_text}"
    try:
        requests.post(PROXY_WEBHOOK_URL, json={
            "type": "chat_message",
            "payload": {"text": echo_text, "sender": "ai"}
        })
    except: pass

def automatic_inventory_worker():
    print("📦 [Simulator] Worker INVENTAR pornit (Adaugă produse)...")
    while True:
        time.sleep(10)
        try:
            # 1. Modificam existent
            if inventory_db:
                idx = random.randint(0, len(inventory_db)-1)
                inventory_db[idx]["quantity"] = max(0, inventory_db[idx]["quantity"] + random.choice([-0.5, 0.5]))

            # 2. ADAUGAM PRODUS NOU (RESTAURAT)
            if random.random() > 0.5:
                new_id = len(inventory_db) + 1
                names = ["Salam", "Ciuperci", "Măsline", "Busuioc", "Ulei", "Drojdie", "Lapte", "Oua"]
                prod_name = random.choice(names)
                
                new_item = {
                    "id": new_id,
                    "product_name": f"{prod_name} (Lot {random.randint(1,99)})",
                    "category": "ingredient",
                    "quantity": float(random.randint(5, 50)),
                    "unit": "buc",
                    "min_threshold": 5.0,
                    "expiration_date": "2025-12-30",
                    "auto_buy": 0
                }
                inventory_db.append(new_item)
                print(f"⚡ [Simulator] Adaugat: {new_item['product_name']}")

            # 3. Trimitem update
            requests.post(PROXY_WEBHOOK_URL, json={
                "type": "data_update",
                "payload": {"category": "inventory", "items": list(inventory_db)}
            })
        except Exception as e: 
            print(f"Eroare worker inventar: {e}")

def automatic_notification_worker():
    while True:
        time.sleep(25)
        try:
            requests.post(PROXY_WEBHOOK_URL, json={"type": "notification", "payload": {"title": "Alertă", "desc": "Verifică stoc.", "type": "info"}})
        except: pass

if __name__ == '__main__':
    threading.Thread(target=automatic_inventory_worker, daemon=True).start()
    threading.Thread(target=automatic_notification_worker, daemon=True).start()
    print("🤖 SIMULATOR REPARAT pornit pe 5001")
    app.run(port=5001, debug=True, use_reloader=False)