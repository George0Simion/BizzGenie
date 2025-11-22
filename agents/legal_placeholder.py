import sys
import os
from flask import Flask, request, jsonify
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.comms import send_json_to_service

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)

@app.route("/send", methods=["POST"])
def legal_endpoint():
    data = request.json
    print(f"⚖️ Legal Agent received: {data}")
    
    # Simulate processing
    subject = data.get("subject", "Unknown")
    
    # Response logic
    response = {
        "status": "success",
        "legal_advice": f"Checked regulations regarding: {subject}. Compliance verified."
    }
    
    return jsonify(response)

if __name__ == "__main__":
    print("⚖️ Legal Agent running on port 5003")
    app.run(port=5003, debug=True)