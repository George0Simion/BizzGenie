# comms.py
import requests

# Where each service runs
SERVICE_URLS = {
    "orchestrator": "http://127.0.0.1:5001",
    "legal": "http://127.0.0.1:5002",
    "predictor": "http://127.0.0.1:5003",
    "financial": "http://127.0.0.1:5004",
    "frontend": "http://127.0.0.1:5005",
}


def send_json_to_service(service_name: str, path: str, payload: dict, timeout: int = 5):
    """
    Send JSON to another service.

    Example:
        send_json_to_service("legal", "/send", {"foo": 1})
        -> POST http://127.0.0.1:5002/send with body {"foo": 1}
    """
    base = SERVICE_URLS.get(service_name)
    if not base:
        return {"error": f"Unknown service '{service_name}'"}

    url = base + path

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
    except requests.RequestException as e:
        return {"error": str(e), "target": url}

    # If you just care “it got there”, reaching this point is already good.
    # But we also try to parse response as JSON:
    try:
        return resp.json()
    except ValueError:
        return {"status_code": resp.status_code, "raw_response": resp.text}
