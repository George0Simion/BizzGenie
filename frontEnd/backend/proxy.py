from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import threading
import time

app = Flask(__name__)
CORS(app)

PROXY_PORT = 5000

# --- FIX 1: URL Corect (Sincronizat cu Simulatorul) ---
TARGET_URL = "http://localhost:5001/process" 
INVENTORY_URL = "http://localhost:5002/inventory"

PENDING_UPDATES = []

# --- THREAD POLLER ---
def inventory_poller():
    while True:
        try:
            resp = requests.get(INVENTORY_URL, timeout=2) # Timeout mic
            try:
                inv_data = resp.json()
            except:
                inv_data = {}

            msg = {
                "type": "data_update",
                "payload": {
                    "category": "inventory",
                    "items": inv_data.get("inventory", [])
                }
            }
            global PENDING_UPDATES
            PENDING_UPDATES.append(msg)
        except:
            pass
        time.sleep(10)

# --- CHAT ---
@app.route('/api/chat', methods=['POST'])
def handle_chat():
    try:
        data = request.json or {}
        user_message = data.get("message", "")
        context = data.get("context", {})

        # Payload acceptat de Simulator ('message' sau 'msg')
        payload = {
            "message": user_message, 
            "msg": user_message,
            "context": context
        }

        print(f"1️⃣ [Proxy] Chat -> Simulator ({TARGET_URL})")
        
        try:
            # --- FIX 2: TIMEOUT (Evita blocarea la infinit) ---
            requests.post(TARGET_URL, json=payload, timeout=5)
        except requests.exceptions.Timeout:
            print("❌ [Proxy] Timeout: Simulatorul nu a răspuns în 5s.")
            return jsonify({"error": "simulator timeout"}), 504
        except Exception as e:
            print(f"❌ [Proxy] Eroare conexiune: {e}")
            return jsonify({"error": "simulator unreachable"}), 502

        return jsonify({"status": "sent"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- WEBHOOK ---
@app.route('/internal/receive', methods=['POST'])
def receive_internal():
    global PENDING_UPDATES
    try:
        data = request.json or {}
        PENDING_UPDATES.append(data)
        return jsonify({"status": "queued"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/from_orchestrator', methods=['POST'])
def from_orchestrator():
    return receive_internal()

# --- POLLING ---
@app.route('/api/updates', methods=['GET'])
def get_updates():
    global PENDING_UPDATES
    if PENDING_UPDATES:
        to_send = list(PENDING_UPDATES)
        PENDING_UPDATES.clear()
        return jsonify({"updates": to_send})
    return jsonify({"updates": []})

# --- SAVE LEGAL ---
@app.route('/api/legal/save', methods=['POST'])
def handle_save_legal():
    try:
        data = request.json
        print("💾 [Proxy] Save Legal -> Simulator...")
        
        # --- FIX 3: Timeout si aici ---
        try:
            requests.post("http://localhost:5001/legal/save", json=data, timeout=5)
            return jsonify({"status": "saved"})
        except requests.exceptions.Timeout:
            print("❌ [Proxy] Save Timeout!")
            return jsonify({"error": "timeout"}), 504
            
    except Exception as e:
        print(f"❌ Eroare Save: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"🚀 PROXY REPARAT pornit pe {PROXY_PORT}")
    t = threading.Thread(target=inventory_poller, daemon=True)
    t.start()
    app.run(port=PROXY_PORT, debug=True, use_reloader=False)