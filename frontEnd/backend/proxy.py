from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import threading
import time

app = Flask(__name__)
CORS(app)

# Porturile
PROXY_PORT = 5000
PROXY_HOST = "0.0.0.0"

# Trimitem către ORCHESTRATOR
TARGET_URL = "http://localhost:5001/text"

# Endpointul serviciului de inventory (schimbă dacă e alt port / path)
INVENTORY_URL = "http://localhost:5002/inventory"

# Coada de mesaje pentru Frontend (Polling)
PENDING_UPDATES = []


# --- THREAD: POLLER INVENTORY LA 10s ---
def inventory_poller():
    """
    Rulează într-un thread separat.
    La fiecare 10 secunde:
      - face request la serviciul de inventory
      - pune rezultatul în PENDING_UPDATES, pe care UI îl ia prin /api/updates
    """
    while True:
        try:
            print("\n🕒 [InventoryPoller] Cer inventory...")
            resp = requests.get(INVENTORY_URL, timeout=5)
            print(f"   [InventoryPoller] HTTP {resp.status_code}")

            # Încearcă să parsezi JSON
            try:
                inv_data = resp.json()
            except Exception:
                inv_data = {"raw": resp.text}
                print("   [InventoryPoller] Răspuns non-JSON, salvez ca 'raw'.")

            # Normalizăm într-un mesaj pe care UI îl poate afișa
            # Frontend-ul așteaptă type=data_update cu payload.category=inventory și items=[]
            msg = {
                "type": "data_update",
                "payload": {
                    "category": "inventory",
                    "items": inv_data.get("inventory", []) if isinstance(inv_data, dict) else [],
                    "status": inv_data.get("status") if isinstance(inv_data, dict) else None
                }
            }

            global PENDING_UPDATES
            PENDING_UPDATES.append(msg)
            print(f"   [InventoryPoller] Inventory pus în coadă. Size = {len(PENDING_UPDATES)}")

        except Exception as e:
            print(f"❌ [InventoryPoller] Eroare la request inventory: {e}")

        time.sleep(10)  # așteaptă 10 secunde


# --- 1. PRIMIM DE LA REACT -> TRIMITEM LA ORCHESTRATOR ---
@app.route('/api/chat', methods=['POST'])
def handle_chat():
    try:
        data = request.json or {}
        print("\n=================== /api/chat ===================")
        print(f"1️⃣ [Proxy] Primit de la React: {json.dumps(data, ensure_ascii=False)}")

        user_message = data.get("message", "")
        context = data.get("context", {}) or {}

        if not user_message:
            print("⚠️ [Proxy] Nu exista campul 'message' sau este gol.")
            return jsonify({"error": "missing 'message' field"}), 400

        orchestrator_payload = {
            "msg": user_message,
            "context": context
        }

        print(f"2️⃣ [Proxy] Forwarding catre Orchestrator ({TARGET_URL}) cu payload:")
        print(f"   {json.dumps(orchestrator_payload, ensure_ascii=False)}")

        try:
            resp = requests.post(TARGET_URL, json=orchestrator_payload, timeout=15)
            print(f"3️⃣ [Proxy] Raspuns HTTP de la Orchestrator: {resp.status_code}")
            try:
                print(f"   Body JSON: {resp.json()}")
            except Exception:
                print(f"   Body (raw): {resp.text[:500]}")
        except Exception as e:
            print(f"❌ [Proxy] Eroare la POST catre Orchestrator ({TARGET_URL}): {e}")
            return jsonify({"error": "orchestrator unreachable"}), 502

        # ACK simplu către React; răspunsul real vine async prin /from_orchestrator sau /internal/receive
        return jsonify({"status": "sent_to_orchestrator"})

    except Exception as e:
        print(f"❌ [Proxy] Eroare in handle_chat: {e}")
        return jsonify({"error": str(e)}), 500


# --- 2. PRIMIM DE LA ORCHESTRATOR (chatbox_response sau data_update) -> NORMALIZAM -> COADA ---
@app.route('/from_orchestrator', methods=['POST'])
def from_orchestrator():
    global PENDING_UPDATES
    try:
        data = request.json or {}
        print("\n=================== /from_orchestrator ===================")
        print(f"3️⃣ [Proxy] Primit de la Orchestrator: {json.dumps(data, ensure_ascii=False)}")

        msg_type = data.get("type")
        sender = data.get("sender", "ai")

        if msg_type == "chatbox_response":
            text = data.get("text", "")

            normalized = {
                "type": "chat_message",
                "payload": {
                    "text": text,
                    "sender": sender
                }
            }
            print(f"   🔄 Normalized to chat_message: {json.dumps(normalized, ensure_ascii=False)}")
            PENDING_UPDATES.append(normalized)
        elif msg_type == "data_update":
            payload = data.get("payload", {})
            category = payload.get("category")
            print(f"   🔄 Data update received. Category={category}")
            PENDING_UPDATES.append({
                "type": "data_update",
                "payload": payload
            })
        else:
            print("   ℹ️ Tip necunoscut, il punem brut in coada.")
            PENDING_UPDATES.append(data)

        print(f"   [Proxy] PENDING_UPDATES size = {len(PENDING_UPDATES)}")
        return "", 204

    except Exception as e:
        print(f"❌ [Proxy] Eroare in /from_orchestrator: {e}")
        return jsonify({"error": str(e)}), 500


# --- 3. ENDPOINT GENERIC (optional) ---
@app.route('/internal/receive', methods=['POST'])
def receive_internal():
    global PENDING_UPDATES
    try:
        data = request.json or {}
        print("\n=================== /internal/receive ===================")
        print(f"📦 [Proxy] Primit generic async: {json.dumps(data, ensure_ascii=False)}")

        PENDING_UPDATES.append(data)
        print(f"   [Proxy] PENDING_UPDATES size = {len(PENDING_UPDATES)}")
        return jsonify({"status": "queued"})
    except Exception as e:
        print(f"❌ [Proxy] Eroare in /internal/receive: {e}")
        return jsonify({"error": str(e)}), 500


# --- 4. REACT CERE NOUTATI (POLLING) ---
@app.route('/api/updates', methods=['GET'])
def get_updates():
    global PENDING_UPDATES
    print("\n=================== /api/updates ===================")
    if PENDING_UPDATES:
        to_send = list(PENDING_UPDATES)
        PENDING_UPDATES.clear()
        print(f"4️⃣ [Proxy] Livrez {len(to_send)} mesaje catre React.")
        print(f"   📦 {json.dumps(to_send, ensure_ascii=False)}")
        return jsonify({"updates": to_send})

    print("4️⃣ [Proxy] Niciun mesaj nou pentru React.")
    return jsonify({"updates": []})


if __name__ == '__main__':
    print(f"🚀 PROXY pornit pe {PROXY_HOST}:{PROXY_PORT}")
    print(f"🔗 Target setat la: {TARGET_URL}")
    print(f"📦 Inventory URL: {INVENTORY_URL}")

    # Pornim poller-ul de inventory într-un thread separat
    t = threading.Thread(target=inventory_poller, daemon=True)
    t.start()

    app.run(host=PROXY_HOST, port=PROXY_PORT, debug=True, use_reloader=False)
