from flask import Flask, request, jsonify
import requests
import threading
import time
import random

app = Flask(__name__)

# Adresa Proxy-ului (Webhook-ul unde trimitem datele asincrone)
PROXY_WEBHOOK_URL = "http://localhost:5000/internal/receive"

# Baza de date simulata (o tinem in memorie)
inventory_db = [
    {"id": 1, "name": "Făină Pizza", "stock": 25, "unit": "kg"},
    {"id": 2, "name": "Sos Roșii", "stock": 10, "unit": "L"},
    {"id": 3, "name": "Mozzarella", "stock": 5, "unit": "kg"}
]

# ==========================================
# 1. AGENTUL HARNIC (AUTO-INVENTAR)
# ==========================================
def automatic_inventory_worker():
    """
    Rulează infinit în fundal.
    La fiecare 10 secunde, adaugă un produs random și trimite update la UI.
    """
    print("📦 [Simulator] Agentul de Inventar a pornit...")
    
    while True:
        time.sleep(10) # Asteapta 10 secunde intre update-uri
        
        # 1. Generam o modificare fictiva
        new_id = len(inventory_db) + 1
        names = ["Salam Picant", "Ciuperci", "Măsline", "Busuioc", "Ulei Măsline", "Drojdie"]
        item_name = random.choice(names)
        
        new_item = {
            "id": new_id,
            "name": f"{item_name} (Lot {random.randint(100,999)})",
            "stock": random.randint(5, 50),
            "unit": "buc"
        }
        
        inventory_db.append(new_item)
        print(f"⚡ [Simulator] Am adăugat automat: {new_item['name']}")

        # 2. Construim pachetul DATA_UPDATE
        payload = {
            "type": "data_update",
            "payload": {
                "category": "inventory",
                "items": list(inventory_db) # Trimitem toata lista actualizata
            }
        }

        # 3. Trimitem la Proxy
        try:
            requests.post(PROXY_WEBHOOK_URL, json=payload)
        except:
            print("❌ [Simulator] Nu pot contacta Proxy-ul (pentru inventar).")


# ==========================================
# 2. AGENTUL PAPAGAL (CHAT ECHO)
# ==========================================
def chat_response_worker(user_text):
    """
    Simuleaza procesarea unui mesaj de la user.
    """
    print(f"⏳ [Simulator] Procesez mesajul: '{user_text}'...")
    time.sleep(2) # Simuleaza gandirea (2 secunde)

    # Construim raspunsul text
    reply_text = f"Răspuns Server: Am primit cu succes mesajul tău: '{user_text}'. Totul funcționează!"

    # Construim pachetul CHAT_MESSAGE
    payload = {
        "type": "chat_message",
        "payload": {
            "text": reply_text,
            "sender": "ai"
        }
    }

    print(f"🚀 [Simulator] Trimit răspuns chat la Proxy.")
    try:
        requests.post(PROXY_WEBHOOK_URL, json=payload)
    except:
        print("❌ [Simulator] Nu pot contacta Proxy-ul (pentru chat).")


# ==========================================
# 3. SERVERUL HTTP (ASCULTA COMENZI)
# ==========================================
@app.route('/process', methods=['POST'])
def handle_request():
    data = request.json
    
    # React trimite cheia 'message', dar verificam si 'msg' pentru siguranta
    user_text = data.get('message') or data.get('msg') or ""
    
    print(f"📩 [Simulator] Request primit de la User: '{user_text}'")

    # Pornim worker-ul de chat pe un fir separat (ca sa nu blocam serverul)
    thread = threading.Thread(target=chat_response_worker, args=(user_text,))
    thread.start()

    return jsonify({"status": "processing"})


if __name__ == '__main__':
    # Pornim firul de executie pentru inventar (ruleaza non-stop)
    threading.Thread(target=automatic_inventory_worker, daemon=True).start()
    
    print("🤖 SIMULATOR COMPLET (Chat + Inventar) pornit pe 5001")
    # use_reloader=False este CRITIC ca sa nu avem dubluri
    app.run(port=5001, debug=True, use_reloader=False)