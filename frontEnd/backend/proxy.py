from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Activează CORS pentru a permite Frontend-ului (port 5173) să vorbească cu noi
CORS(app)

# --- CONFIGURARE ---
# Portul pe care rulează PROXY-ul
PROXY_PORT = 5000

# Adresa serverului TAU (Target / Orchestrator / LLM)
# Aici trimitem mesajele din chat
TARGET_SERVER_URL = "http://localhost:5001/process"


# --- MEMORIE TEMPORARĂ ---
# Aici stocăm mesajele/datele venite asincron de la Target
# până când Frontend-ul vine să le ceară (Polling).
PENDING_UPDATES_QUEUE = []


# ==================================================================
# 1. FLUXUL DIRECT: CHAT (Frontend -> Proxy -> Target -> Frontend)
# ==================================================================
@app.route('/api/chat', methods=['POST'])
def handle_chat_message():
    try:
        # A. Primim mesajul de la User (Frontend)
        frontend_data = request.json
        user_message = frontend_data.get('message')
        context = frontend_data.get('context', {})

        print(f"1️⃣ [Proxy] Primit de la React: {user_message}")

        # B. Trimitem mai departe la Target
        payload = {
            "msg": user_message,
            "context": context
        }
        
        try:
            print(f"2️⃣ [Proxy] Forwarding catre Target ({TARGET_SERVER_URL})...")
            target_response = requests.post(TARGET_SERVER_URL, json=payload, timeout=60)
            target_data = target_response.json()
            
            # C. Returnăm răspunsul imediat al Target-ului (dacă există)
            # De obicei un mesaj de confirmare sau răspunsul direct la chat
            return jsonify(target_data)

        except requests.exceptions.ConnectionError:
            return jsonify({
                "text": "Eroare: Serverul Target (AI) nu răspunde.", 
                "sender": "system"
            }), 503

    except Exception as e:
        print(f"❌ Eroare Proxy Chat: {e}")
        return jsonify({"error": str(e)}), 500


# ==================================================================
# 2. FLUXUL INVERS: TARGET -> PROXY (Webhook intern)
# ==================================================================
# Aceasta este ruta unde Target-ul trimite date când vrea el.
# Target-ul va face un POST aici cu un JSON care specifică TIPUL datelor.
@app.route('/internal/receive', methods=['POST'])
def receive_from_target():
    global PENDING_UPDATES_QUEUE
    
    try:
        data = request.json
        
        # Validare simplă
        if not data:
            return jsonify({"status": "error", "msg": "No data provided"}), 400

        # Logare pentru debug
        data_type = data.get('type', 'unknown')
        print(f"📥 [Proxy] Primit date asincrone de la Target. Tip: {data_type}")
        
        # Adăugăm în coadă pentru a fi ridicate de Frontend
        PENDING_UPDATES_QUEUE.append(data)
        
        return jsonify({"status": "success", "msg": "Data queued for frontend"}), 200

    except Exception as e:
        print(f"❌ Eroare Internal Receive: {e}")
        return jsonify({"error": str(e)}), 500


# ==================================================================
# 3. FLUXUL DE POLLING: FRONTEND -> PROXY (Verificare noutăți)
# ==================================================================
# Frontend-ul apelează ruta asta la fiecare X secunde
@app.route('/api/updates', methods=['GET'])
def check_for_updates():
    global PENDING_UPDATES_QUEUE
    
    # Dacă avem date în coadă
    if PENDING_UPDATES_QUEUE:
        # Facem o copie a listei ca să o trimitem
        updates_to_send = list(PENDING_UPDATES_QUEUE)
        
        # Golim coada originală
        PENDING_UPDATES_QUEUE.clear()
        
        print(f"📤 [Proxy] Livrat {len(updates_to_send)} update-uri către Frontend.")
        return jsonify({"updates": updates_to_send})
    
    # Dacă nu e nimic nou
    else:
        return jsonify({"updates": []})


if __name__ == '__main__':
    print(f"🚀 Proxy Server pornit pe portul {PROXY_PORT}")
    print(f"🔗 Target setat la: {TARGET_SERVER_URL}")
    app.run(port=PROXY_PORT, debug=True)