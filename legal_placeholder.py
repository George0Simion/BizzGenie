# legal.py
from flask import Flask, request, jsonify
from comms import send_json_to_service
app = Flask(__name__)
SERVICE_NAME = "legal"


@app.route("/send", methods=["POST"])
def receive_from_any_service():
    """
    Any service can POST JSON here:
      POST http://127.0.0.1:500/send
    """
    data = request.get_json(silent=True) or {}
    print(f"[{SERVICE_NAME}] /send received:", data)

    # Do your processing here
     #data contains params

    print(f"data received: {data}")
    work()
    
    result = {
        "service": SERVICE_NAME,
        "received": data,
        "legal_ok": True,
        "info": "checked by legal"
    }

    # By returning 200, we signal "I got it and processed it"
    return jsonify(result), 200



def work():

    import time
    time.sleep(10)  # Simulate doing something useful
        
    send_json_to_service(
        "orchestrator",
        "/legal",
        {"status": "legal work completed"}
    )




if __name__ == "__main__":
    app.run(port=5003, debug=True)