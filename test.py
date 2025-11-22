import requests
import time

# Target the Orchestrator
URL = "http://127.0.0.1:5001/message"

def test_orchestrator():
    print("🚀 Sending message to Orchestrator...")
    
    payload = {
        "message": "I just bought 5kg of cherries for the restaurant."
    }
    
    try:
        response = requests.post(URL, json=payload)
        print("\n✅ SYSTEM RESPONSE STATUS:", response.status_code)
        
        data = response.json()
        
        print("\n📋 ORCHESTRATOR PLAN:")
        print(data.get("orchestrator_plan"))
        
        print("\n🍅 INVENTORY AGENT SAID:")
        print(data.get("agent_results", {}).get("inventory", {}).get("response_text"))
        
        print("\n⚖️ LEGAL AGENT SAID:")
        print(data.get("agent_results", {}).get("legal"))

    except Exception as e:
        print("❌ Connection Failed. Are all 3 terminals running?", e)

if __name__ == "__main__":
    test_orchestrator()