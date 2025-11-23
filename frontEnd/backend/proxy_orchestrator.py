from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json
import threading
import time

app = Flask(__name__)
CORS(app)

# ==========================================
# CONFIGURARE
# ==========================================
PROXY_PORT = 5000

# Adresa Orchestratorului Tău (Codul furnizat de tine)
ORCHESTRATOR_BASE_URL = "http://localhost:5001"
ORCHESTRATOR_CHAT_URL = f"{ORCHESTRATOR_BASE_URL}/text"
ORCHESTRATOR_UPLOAD_URL = f"{ORCHESTRATOR_BASE_URL}/upload" # Dacă vei implementa upload
ORCHESTRATOR_LEGAL_SAVE_URL = f"{ORCHESTRATOR_BASE_URL}/legal/save" # Dacă vei implementa save
ORCHESTRATOR_FILES_URL = f"{ORCHESTRATOR_BASE_URL}/files"

# Adresa serviciului de Inventory (Independent)
INVENTORY_SERVICE_URL = "http://localhost:5002/inventory"

# Coada de mesaje pentru Frontend (Polling)
PENDING_UPDATES = []


# ==========================================
# THREAD DE FUNDAL: POLLER INVENTORY
# ==========================================
def inventory_poller():
    """
    Verifică periodic serviciul de inventar (5002) și trimite update-uri la UI.
    Acesta rulează independent de Orchestrator.
    """
    while True:
        try:
            resp = requests.get(INVENTORY_SERVICE_URL, timeout=2)
            try:
                inv_data = resp.json()
            except:
                inv_data = {}

            # Normalizam datele pentru Frontend
            items = inv_data.get("inventory", [])
            
            if items: 
                msg = {
                    "type": "data_update",
                    "payload": {
                        "category": "inventory",
                        "items": items
                    }
                }
                global PENDING_UPDATES
                PENDING_UPDATES.append(msg)
                
        except Exception:
            pass # Ignoram erorile de conexiune la inventory

        time.sleep(5)


# ==========================================
# RUTE API (FRONTEND -> PROXY)
# ==========================================

# 1. CHAT: Trimitem mesajul utilizatorului catre Orchestrator
@app.route('/api/chat', methods=['POST'])
def handle_chat():
    try:
        data = request.json or {}
        user_message = data.get("message", "")
        context = data.get("context", {})

        if not user_message:
            return jsonify({"error": "missing message"}), 400

        # Pachetul formatat pentru Orchestrator (asteapta 'msg' sau 'text')
        payload = {
            "msg": user_message, 
            "text": user_message, # Backup key
            "context": context
        }

        print(f"1️⃣ [Proxy] Chat -> Orchestrator ({ORCHESTRATOR_CHAT_URL})...")

        try:
            # Orchestratorul returneaza 204 sau un ACK rapid
            requests.post(ORCHESTRATOR_CHAT_URL, json=payload, timeout=10)
        except Exception as e:
            print(f"❌ [Proxy] Eroare conexiune Orchestrator: {e}")
            return jsonify({"error": "orchestrator unreachable"}), 502

        return jsonify({"status": "sent"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 2. UPLOAD DOCUMENT
@app.route('/api/upload', methods=['POST'])
def handle_upload():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        
        files = {'file': (file.filename, file.stream, file.content_type)}
        
        try:
            # Încercăm să trimitem la Orchestrator (chiar dacă nu are logica încă)
            requests.post(ORCHESTRATOR_UPLOAD_URL, files=files, timeout=10)
            return jsonify({"status": "uploaded"})
        except Exception:
            # Returnăm success ca UI-ul să nu crape
            return jsonify({"status": "simulated_success", "warning": "orchestrator_upload_failed"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 3. SAVE LEGAL
@app.route('/api/legal/save', methods=['POST'])
def handle_save_legal():
    try:
        data = request.json
        print("\n💾 [Proxy] Forwarding Save Legal...")
        requests.post(ORCHESTRATOR_LEGAL_SAVE_URL, json=data, timeout=5)
        return jsonify({"status": "saved"})
    except Exception:
        # Returnam success fals ca sa nu ramana butonul blocat in loading
        return jsonify({"status": "saved_offline"}), 200


# 4. DOWNLOAD FILE
@app.route('/api/files/<path:filename>', methods=['GET'])
def handle_download(filename):
    try:
        target_url = f"{ORCHESTRATOR_FILES_URL}/{filename}"
        req = requests.get(target_url, stream=True)
        return Response(req.iter_content(chunk_size=1024), 
                        content_type=req.headers.get('Content-Type'))
    except Exception:
        return jsonify({"error": "File not found"}), 404


# ==========================================
# RUTE INTERNE (ORCHESTRATOR -> PROXY -> FRONTEND)
# ==========================================

# 5. PRIMIRE DATE DE LA ORCHESTRATOR (Ruta specificata in codul tau Python)
@app.route('/from_orchestrator', methods=['POST'])
def from_orchestrator():
    global PENDING_UPDATES
    try:
        data = request.json or {}
        print(f"📥 [Proxy] Primit de la Orchestrator: {json.dumps(data)}")

        # --- LOGICA DE NORMALIZARE (TRADUCERE) ---
        # Orchestratorul trimite: { "type": "chatbox_response", "text": "..." }
        # Frontend-ul asteapta:   { "type": "chat_message", "payload": { "text": "...", "sender": "ai" } }
        
        msg_type = data.get("type")
        
        if msg_type == "chatbox_response":
            normalized_msg = {
                "type": "chat_message",
                "payload": {
                    "text": data.get("text", ""),
                    "sender": "ai"
                }
            }
            PENDING_UPDATES.append(normalized_msg)
            print("   ✅ Convertit in format Frontend (chat_message)")
            
        elif msg_type == "data_update":
            # Daca orchestratorul trimite deja formatul corect (ex: legal update din functia legal_recieve)
            PENDING_UPDATES.append(data)
            print("   ✅ Date pasate direct")
            
        else:
            # Orice altceva
            PENDING_UPDATES.append(data)

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"❌ Eroare procesare date de la Orchestrator: {e}")
        return jsonify({"error": str(e)}), 500


# 6. WEBHOOK GENERIC
@app.route('/internal/receive', methods=['POST'])
def receive_internal():
    return from_orchestrator()


# 7. POLLING (Frontend cere noutati)
@app.route('/api/updates', methods=['GET'])
def get_updates():
    global PENDING_UPDATES
    if PENDING_UPDATES:
        to_send = list(PENDING_UPDATES)
        PENDING_UPDATES.clear()
        print(f"📤 [Proxy] Livrez {len(to_send)} mesaje catre React.")
        return jsonify({"updates": to_send})

    return jsonify({"updates": []})


if __name__ == '__main__':
    print(f"🚀 PROXY SPECIAL (ORCHESTRATOR) pornit pe portul {PROXY_PORT}")
    print(f"🔗 Legat de Orchestrator la: {ORCHESTRATOR_BASE_URL}")
    
    # Pornim poller-ul pentru inventar
    t = threading.Thread(target=inventory_poller, daemon=True)
    t.start()

    app.run(port=PROXY_PORT, debug=True, use_reloader=False)