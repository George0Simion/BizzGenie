import requests
import json

# URL for Orchestrator
BASE_URL = "http://127.0.0.1:5001"

def test_full_flow():
    print("🚀 1. Sending 'Add' message to Orchestrator...")
    msg_payload = {"message": "I bought 10kg of potatoes and 5 liters of milk"}
    
    try:
        resp = requests.post(f"{BASE_URL}/message", json=msg_payload)
        print("  Orchestrator Reply:", resp.status_code)
        # print(json.dumps(resp.json(), indent=2))
    except Exception as e:
        print("  Failed:", e)
        return

    print("\n🚀 2. Fetching Full Inventory via Orchestrator...")
    try:
        resp = requests.get(f"{BASE_URL}/get-inventory")
        data = resp.json()
        
        print(f"📦 Total Items in Stock: {data.get('count', 0)}")
        print("📋 Inventory List:")
        for item in data.get("inventory", []):
            print(f"   - {item['product_name']}: {item['quantity']}{item['unit']} (Exp: {item['expiration_date']}) [{item['category']}]")
            
    except Exception as e:
        print("  Failed to fetch inventory:", e)

if __name__ == "__main__":
    test_full_flow()