from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --------------------------
# 1. SEND JSON TO ORCHESTRATOR
# --------------------------
def send_json_to_orchestrator(payload: dict):
    """
    Trimite un JSON către orchestrator la ruta /text.
    """
    url = "http://localhost:5001/text"

    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"[proxy] Sent to orchestrator ({url}): {payload}")
        print(f"[proxy] Orchestrator responded with: {resp.status_code}")
        return True
    except Exception as e:
        print(f"[proxy] ERROR sending JSON to orchestrator: {e}")
        return False


# --------------------------
# 2. RECEIVE JSON FROM ORCHESTRATOR
# --------------------------
@app.route('/from_orchestrator', methods=['POST'])
def receive_json_from_orchestrator():
    """
    Endpointul care primește JSON trimis de orchestrator.
    """
    try:
        data = request.json or {}
        print(f"[proxy] Received JSON from orchestrator: {data}")

        # aici adaugi TU orice logică ai nevoie:
        #   - queue
        #   - push to frontend
        #   - store for polling
        #   - immediate return on /api/chat
        # etc.

        return "", 204
    except Exception as e:
        print(f"[proxy] ERROR receiving JSON from orchestrator: {e}")
        return jsonify({"error": str(e)}), 500


# --------------------------
# 4. RUN APP
# --------------------------
if __name__ == "__main__":
    print("Proxy running on port 5000")
    app.run(port=5000, debug=True)
