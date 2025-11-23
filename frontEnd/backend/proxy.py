from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# Porturile
PROXY_PORT = 5000
TARGET_URL = "http://localhost:5001/process"

# Coada de mesaje pentru Frontend (Polling)
PENDING_UPDATES = []

# --- 1. PRIMIM DE LA REACT -> TRIMITEM LA SIMULATOR ---
@app.route('/api/chat', methods=['POST'])
def handle_chat():
    try:
        # Logam ce am primit de la React
        data = request.json
        print(f"\n1️⃣ [Proxy] Primit de la React: {json.dumps(data)}")

        # Trimitem exact acelasi lucru mai departe la Simulator
        # React trimite: { "message": "Salut", "context": {...} }
        print(f"2️⃣ [Proxy] Forwarding catre Simulator ({TARGET_URL})...")
        
        try:
            requests.post(TARGET_URL, json=data, timeout=5)
        except:
            print("❌ [Proxy] Simulatorul nu raspunde (5001)!")

        # Returnam OK la React (nu asteptam raspunsul final aici)
        return jsonify({"status": "sent_to_simulator"})

    except Exception as e:
        print(f"❌ Eroare Proxy: {e}")
        return jsonify({"error": str(e)}), 500


# --- 2. PRIMIM DE LA SIMULATOR -> SALVAM PENTRU REACT ---
@app.route('/internal/receive', methods=['POST'])
def receive_internal():
    global PENDING_UPDATES
    data = request.json
    
    print(f"3️⃣ [Proxy] Primit raspuns ASINCRON de la Simulator:")
    print(f"   📦 {json.dumps(data)}")
    
    PENDING_UPDATES.append(data)
    return jsonify({"status": "queued"})


# --- 3. REACT CERE NOUTATI (POLLING) ---
@app.route('/api/updates', methods=['GET'])
def get_updates():
    global PENDING_UPDATES
    if PENDING_UPDATES:
        print(f"4️⃣ [Proxy] Livrez {len(PENDING_UPDATES)} mesaje catre React.")
        to_send = list(PENDING_UPDATES)
        PENDING_UPDATES.clear()
        return jsonify({"updates": to_send})
    
    return jsonify({"updates": []})

if __name__ == '__main__':
    print(f"🚀 PROXY pornit pe portul {PROXY_PORT}")
    app.run(port=PROXY_PORT, debug=True, use_reloader=False)
