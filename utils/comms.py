import requests

# DEFINING THE PORTS CLEARLY
SERVICE_URLS = {
    "orchestrator": "http://127.0.0.1:5001",
    "inventory":    "http://127.0.0.1:5002", # Fixed Port
    "legal":        "http://127.0.0.1:5003", # Moved to 5003 to avoid conflict
}

def send_json_to_service(service_name: str, path: str, payload: dict, timeout: int = 10):
    base = SERVICE_URLS.get(service_name)
    if not base:
        print(f"❌ Service {service_name} not defined in SERVICE_URLS")
        return {"error": f"Unknown service '{service_name}'"}

    url = base + path
    print(f"📡 Sending to {service_name}: {url}")

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"❌ Error contacting {service_name}: {e}")
        return {"error": str(e)}