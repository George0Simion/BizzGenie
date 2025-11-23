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

# Unde trimitem comenzile (Către Simulator pe 5001)
TARGET_CHAT_URL = "http://localhost:5001/process"
TARGET_UPLOAD_URL = "http://localhost:5001/upload"
TARGET_LEGAL_SAVE_URL = "http://localhost:5001/legal/save"
TARGET_FILE_URL = "http://localhost:5001/files" 

# Endpoint extern pentru inventar (Legacy/Poller - ex: un alt serviciu pe 5002)
INVENTORY_URL = "http://localhost:5002/inventory"

# Coada de mesaje pentru Frontend (Polling)
PENDING_UPDATES = []


# ==========================================
# THREAD DE FUNDAL: POLLER INVENTORY (5002)
# ==========================================
def inventory_poller():
    """
    Verifică periodic un serviciu extern de inventar (port 5002).
    Dacă nu există, ignoră eroarea silențios.
    """
    while True:
        try:
            resp = requests.get(INVENTORY_URL, timeout=2)
            try:
                inv_data = resp.json()
            except:
                inv_data = {}

            msg = {
                "type": "data_update",
                "payload": {
                    "category": "inventory",
                    "items": inv_data.get("inventory", []) if isinstance(inv_data, dict) else []
                }
            }

            global PENDING_UPDATES
            PENDING_UPDATES.append(msg)
        except Exception:
            pass # E ok să eșueze dacă nu ai serverul 5002 pornit

        time.sleep(10)


# ==========================================
# RUTE API (FRONTEND -> PROXY)
# ==========================================

# 1. CHAT
@app.route('/api/chat', methods=['POST'])
def handle_chat():
    try:
        data = request.json or {}
        user_message = data.get("message", "")
        context = data.get("context", {})

        if not user_message:
            return jsonify({"error": "missing message"}), 400

        # Pachetul pentru Simulator
        payload = {
            "message": user_message, 
            "msg": user_message, # Compatibilitate
            "context": context
        }

        print(f"1️⃣ [Proxy] Chat -> Simulator...")

        try:
            # Trimitem la Simulator cu Timeout
            requests.post(TARGET_CHAT_URL, json=payload, timeout=5)
        except requests.exceptions.Timeout:
            print("❌ [Proxy] Timeout Simulator!")
            return jsonify({"error": "simulator timeout"}), 504
        except Exception as e:
            print(f"❌ [Proxy] Eroare Simulator: {e}")
            return jsonify({"error": "simulator unreachable"}), 502

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
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        print(f"📂 [Proxy] Primit fișier: {file.filename}. Trimit la Simulator...")

        # Reîmpachetăm fișierul pentru Simulator
        files = {'file': (file.filename, file.stream, file.content_type)}
        
        try:
            requests.post(TARGET_UPLOAD_URL, files=files, timeout=10)
            return jsonify({"status": "uploaded_to_simulator"})
        except Exception as e:
            print(f"❌ [Proxy] Eroare upload la simulator: {e}")
            return jsonify({"error": "simulator upload failed"}), 502

    except Exception as e:
        print(f"❌ Eroare Upload Proxy: {e}")
        return jsonify({"error": str(e)}), 500


# 3. SAVE LEGAL
@app.route('/api/legal/save', methods=['POST'])
def handle_save_legal():
    try:
        data = request.json
        print("\n💾 [Proxy] Forwarding Save Legal...")
        requests.post(TARGET_LEGAL_SAVE_URL, json=data, timeout=5)
        return jsonify({"status": "saved"})
    except Exception as e:
        print(f"❌ Eroare Save: {e}")
        return jsonify({"error": str(e)}), 500


# 4. DOWNLOAD FILE (Proxy pentru download)
@app.route('/api/files/<path:filename>', methods=['GET'])
def handle_download(filename):
    try:
        # Cerem fișierul de la Simulator (5001)
        simulator_url = f"{TARGET_FILE_URL}/{filename}"
        
        # Facem stream la date
        req = requests.get(simulator_url, stream=True)
        
        return Response(req.iter_content(chunk_size=1024), 
                        content_type=req.headers['Content-Type'])
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# ==========================================
# RUTE INTERNE (SIMULATOR -> PROXY -> FRONTEND)
# ==========================================

# 5. WEBHOOK (Aici Simulatorul trimite date asincrone)
@app.route('/internal/receive', methods=['POST'])
def receive_internal():
    global PENDING_UPDATES
    try:
        data = request.json or {}
        # print(f"📦 [Proxy] Primit Async: {data.get('type')}")
        PENDING_UPDATES.append(data)
        return jsonify({"status": "queued"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta de compatibilitate
@app.route('/from_orchestrator', methods=['POST'])
def from_orchestrator():
    return receive_internal()


# 6. POLLING (Aici React vine să își ia datele)
@app.route('/api/updates', methods=['GET'])
def get_updates():
    global PENDING_UPDATES
    if PENDING_UPDATES:
        to_send = list(PENDING_UPDATES)
        PENDING_UPDATES.clear()
        print(f"4️⃣ [Proxy] Livrez {len(to_send)} mesaje catre React.")
        return jsonify({"updates": to_send})

    return jsonify({"updates": []})


if __name__ == '__main__':
    print(f"🚀 PROXY COMPLET pornit pe portul {PROXY_PORT}")
    
    # Pornim poller-ul pentru 5002
    t = threading.Thread(target=inventory_poller, daemon=True)
    t.start()

    app.run(port=PROXY_PORT, debug=True, use_reloader=False)