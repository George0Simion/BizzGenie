from flask import Flask, request, jsonify
import requests
import threading
import time
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# URL-ul unde trimitem datele către Proxy (Push)
PROXY_WEBHOOK_URL = "http://localhost:5000/internal/receive"

# ==========================================
# DATE INIȚIALE (BAZA DE DATE ÎN MEMORIE)
# ==========================================

# 1. INVENTAR
inventory_db = [
    {
        "id": 1, 
        "product_name": "Tomato", 
        "category": "vegetable", 
        "quantity": 3.0, 
        "unit": "kg", 
        "min_threshold": 5.0, 
        "expiration_date": "2025-12-07", 
        "auto_buy": 0
    },
    {
        "id": 2, 
        "product_name": "Potato", 
        "category": "vegetable", 
        "quantity": 15.0, 
        "unit": "kg", 
        "min_threshold": 2.0, 
        "expiration_date": "2025-12-23", 
        "auto_buy": 1
    }
]

# 2. LEGAL - Lista curentă de task-uri
legal_db = [
    {
        "id": 101, 
        "title": "Înregistrare ONRC", 
        "status": "completed", 
        "description": "Procesul obligatoriu.", 
        "steps": [
            {"step": "Rezervare nume", "done": True}, 
            {"step": "Depunere dosar", "done": True}
        ]
    }
]

# 3. LEGAL RESEARCH - Datele complexe cerute
TOMATO_RESEARCH_DATA = {
  "service": "legal",
  "subject": "Siguranță Alimentară: Roșii",
  "context": {},
  "research": {
    "summary": "Restaurantele trebuie să urmeze reglementările europene și naționale privind siguranța alimentară pentru păstrarea roșiilor.",
    "checklist": [
      {
        "step": "Verifică calitatea la recepție",
        "action": "Examinează roșiile la primire.",
        "citation": "Reg. (CE) nr. 852/2004",
        "source": "https://eur-lex.europa.eu/legal-content/RO/TXT/?uri=celex%3A32004R0852",
        "done": False
      },
      {
        "step": "Aplică trasabilitatea (FIFO)",
        "action": "Notează proveniența și data recepției.",
        "citation": "Reg. (CE) nr. 178/2002",
        "done": False
      },
      {
        "step": "Depozitare Corectă",
        "action": "Păstrează la peste 8°C.",
        "citation": "Ordinul nr. 111/2008",
        "done": False
      }
    ],
    "risks": [
      {"risk": "Contaminare bacteriană", "mitigation": "Respectă igiena."},
      {"risk": "Amendă DSP", "mitigation": "Documentează loturile."}
    ]
  }
}

# ==========================================
# WORKERS (PROCESE DE FUNDAL)
# ==========================================

def automatic_inventory_worker():
    """
    Simulează activitatea în depozit:
    - Consumă stoc existent.
    - Adaugă produse noi (aprovizionare) la fiecare 10 secunde.
    """
    print("📦 [Simulator] Worker INVENTAR pornit...")
    while True:
        time.sleep(10)
        
        try:
            # A. Modificăm stoc existent (Consum)
            if inventory_db:
                idx = random.randint(0, len(inventory_db) - 1)
                change = random.choice([-0.5, 0.0, 2.0])
                inventory_db[idx]["quantity"] = max(0.0, inventory_db[idx]["quantity"] + change)

            # B. Adăugăm produs nou (Aprovizionare)
            # 70% șanse să vină marfă nouă
            if random.random() > 0.3:
                new_id = len(inventory_db) + 1
                
                # Generăm date random dar realiste
                products = [
                    ("Milk", "dairy", "L"), 
                    ("Eggs", "dairy", "buc"), 
                    ("Flour", "dry", "kg"), 
                    ("Basil", "herb", "buc"),
                    ("Cheese", "dairy", "kg"),
                    ("Ham", "meat", "kg")
                ]
                prod = random.choice(products)
                future_date = datetime.now() + timedelta(days=random.randint(5, 30))
                
                new_item = {
                    "id": new_id,
                    "product_name": f"{prod[0]} (Lot {random.randint(100, 999)})",
                    "category": prod[1],
                    "quantity": float(random.randint(5, 50)),
                    "unit": prod[2],
                    "min_threshold": 5.0,
                    "expiration_date": future_date.strftime("%Y-%m-%d"),
                    "auto_buy": random.choice([0, 1])
                }
                
                inventory_db.append(new_item)
                print(f"📦 [Simulator] Produs adăugat: {new_item['product_name']}")

            # C. Trimitem update-ul la Proxy
            payload = {
                "type": "data_update",
                "payload": {
                    "category": "inventory",
                    "items": list(inventory_db)
                }
            }
            requests.post(PROXY_WEBHOOK_URL, json=payload)
            
        except Exception as e:
            print(f"❌ Eroare Worker Inventar: {e}")


def trigger_complex_legal_research():
    """ Trimite datele de research Legal după 15 secunde (o singură dată) """
    print("⚖️ [Simulator] Agentul Legal analizează legislația...")
    time.sleep(15)
    
    print("⚖️ [Simulator] Research finalizat! Trimit datele...")
    payload = {
        "type": "data_update",
        "payload": {
            "category": "legal_research",
            "data": TOMATO_RESEARCH_DATA
        }
    }
    try:
        requests.post(PROXY_WEBHOOK_URL, json=payload)
        # requests.post(PROXY_WEBHOOK_URL, json={})
        # Trimitem și notificare
        requests.post(PROXY_WEBHOOK_URL, json={
            "type": "notification",
            "payload": {"title": "Research Finalizat", "desc": "Reguli noi pentru roșii.", "type": "info"}
        })
    except: pass


def automatic_notification_worker():
    """ Trimite o notificare random la fiecare 30 secunde """
    while True:
        time.sleep(30)
        alerts = [
            {"title": "Factură Scadentă", "desc": "Factura E-ON expiră mâine.", "type": "warning"},
            {"title": "Client Nemulțumit", "desc": "Review negativ pe Glovo.", "type": "critical"}
        ]
        alert = random.choice(alerts)
        try:
            requests.post(PROXY_WEBHOOK_URL, json={"type": "notification", "payload": alert})
            print(f"🔔 [Simulator] Notificare trimisă: {alert['title']}")
        except: pass


# ==========================================
# RUTE HTTP (API)
# ==========================================

# 1. PROCESARE CHAT
# Proxy-ul tău trimite aici: http://localhost:5001/process
@app.route('/process', methods=['POST'])
def handle_chat_request():
    data = request.json
    # Citim mesajul
    user_text = data.get('message') or data.get('msg') or ""
    
    print(f"📩 [Simulator] Chat primit: '{user_text}'")
    
    # Simulăm răspunsul AI pe un alt thread
    def reply():
        time.sleep(1.5) # Gândește...
        echo_text = f"Echo Server: Am primit mesajul tău '{user_text}' și l-am procesat."
        try:
            requests.post(PROXY_WEBHOOK_URL, json={
                "type": "chat_message",
                "payload": {"text": echo_text, "sender": "ai"}
            })
        except: pass
        
    threading.Thread(target=reply).start()
    return jsonify({"status": "received"})


# 2. SALVARE LEGAL
# Proxy-ul tău trimite aici: http://localhost:5001/legal/save
@app.route('/legal/save', methods=['POST'])
def handle_legal_save():
    global legal_db
    data = request.json
    
    if 'tasks' in data:
        print("💾 [Simulator] Salvare Legal primită.")
        legal_db = data['tasks']
        
        # Confirmare asincronă
        def confirm():
            time.sleep(1)
            requests.post(PROXY_WEBHOOK_URL, json={
                "type": "notification",
                "payload": {"title": "Salvat", "desc": "Modificările au fost înregistrate în sistem.", "type": "info"}
            })
        threading.Thread(target=confirm).start()

    return jsonify({"status": "saved"})


if __name__ == '__main__':
    # Pornim toate procesele de fundal
    threading.Thread(target=automatic_inventory_worker, daemon=True).start()
    threading.Thread(target=trigger_complex_legal_research, daemon=True).start()
    threading.Thread(target=automatic_notification_worker, daemon=True).start()
    
    print("🤖 SIMULATOR COMPLET (Port 5001) - Gata de acțiune!")
    # use_reloader=False previne dublarea workerilor
    app.run(port=5001, debug=True, use_reloader=False)