from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

# All other Flask services you want to talk to
# Key is a name, value is the base URL
UPSTREAM_SERVERS = {
    "orchestrator": "http://127.0.0.1:5001",
    "legal": "http://127.0.0.1:5002",
    "predictor": "http://127.0.0.1:5003",
}


def forward_request(service_name):
    """
    Forward the current Flask request (JSON-only) to the given service
    and return its response.
    """

    if service_name not in UPSTREAM_SERVERS:
        return jsonify({"error": f"Unknown service '{service_name}'"}), 404

    target_base = UPSTREAM_SERVERS[service_name]
    # Change this if your upstream uses a different path than "/"
    target_url = f"{target_base}/"

    try:
        if request.method == "GET":
            # Forward query params
            resp = requests.get(
                target_url,
                params=request.args,
                timeout=5,
            )
        elif request.method == "POST":
            # Forward JSON body
            data = request.get_json(silent=True) or {}
            resp = requests.post(
                target_url,
                json=data,
                params=request.args,
                timeout=5,
            )
        else:
            return jsonify({"error": "Method not supported"}), 405

    except requests.RequestException as e:
        return jsonify({"error": str(e), "target": service_name}), 502

    # Try to return JSON if possible, otherwise raw text
    content_type = resp.headers.get("Content-Type", "")
    if content_type.startswith("application/json"):
        return jsonify(resp.json()), resp.status_code
    else:
        # Pass through other content types as-is
        return Response(resp.content, status=resp.status_code, content_type=content_type)


@app.route("/legal", methods=["POST", "GET"])
def legal():
    return forward_request("legal")


@app.route("/orchestrator", methods=["POST", "GET"])
def orchestrator():
    return forward_request("orchestrator")


@app.route("/predictor", methods=["POST", "GET"])
def predictor():
    return forward_request("predictor")










if __name__ == "__main__":
    # Central broker on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)