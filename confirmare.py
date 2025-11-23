import requests

# --- DATELE TALE EXACTE (HARDCODED) ---
CLIENT_ID = "c80c3a63-58e2-426a-bf39-7db77c23b4af"
CLIENT_SECRET = "D9S1$VE7u)F4AF~gX@QB67g9Au94z@*0z3QRd^!^_CW7TUi(%bAS~$qHnFj0g~$^"

def test_hardcoded():
    print("⏳ Testez credențialele tale...")
    
    url = "https://account.uipath.com/oauth/token"
    
    # Folosim 'data' pentru standardul OAuth
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "OR.Queues.Write"
    }
    
    try:
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            print("\n✅ VICTORIE! Credențialele sunt 100% BUNE.")
            print(f"Token: {response.json()['access_token'][:20]}...")
            print("\nMergi la PASUL 2 și actualizează agentul!")
        else:
            print(f"\n❌ Eroare {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Eroare: {e}")

if __name__ == "__main__":
    test_hardcoded()