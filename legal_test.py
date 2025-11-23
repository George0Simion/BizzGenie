import requests
import json

LEGAL_URL = "http://localhost:5006/documents"   # change this to your legal service port/path

def test_legal():
    payload = {
        "legal": {
            "subject": "inscriere firma la ANAF",
            "context": {}
        }
    }

    print("[TEST] Sending to legal service...")
    resp = requests.post(LEGAL_URL, json=payload, timeout=10)

    print("[TEST] Status:", resp.status_code)

    try:
        data = resp.json()
        print("[TEST] Response JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print("[TEST] Raw response:")
        print(resp.text)

if __name__ == "__main__":
    test_legal()
