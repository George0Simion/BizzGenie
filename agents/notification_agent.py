import requests
import logging
import json
import os
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class NotificationAgent:
    def __init__(self):
        # Endpoint pentru generare token
        self.token_url = "https://cloud.uipath.com/identity_/connect/token"

        # Endpoint pentru Orchestrator
        self.base_url = "https://cloud.uipath.com/persobzhsnqq/DefaultTenant/orchestrator_/odata"

        # 🔑 Cheile aplicației externe din UiPath Cloud
        self.client_id = "bf1351e1-3b4e-482d-8eea-c43aa5188dbf"
        self.client_secret = "pC95NCMwC2T1td1S38W3m!sGEOzBqq1Cs~^aUQrzOO#XeN@Z_GXUsr(C4(u%jXhz"

        self.folder_id = 6870187
        self.queue_name = "AlertsQueue"

    def _get_access_token(self):
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
    }


        try:
            response = requests.post(self.token_url, data=payload)
            response.raise_for_status()
            return response.json()["access_token"]
        except Exception as e:
            logging.error(f"[Auth Error]: {e}, Response: {getattr(response, 'text', '')}")
            return None

    def send_alert(self, email_data):
        token = self._get_access_token()
        if not token:
            logging.error("❌ Nu am token. Oprire.")
            return False

        add_item_url = f"{self.base_url}/Queues/UiPathODataSvc.AddQueueItem"

        headers = {
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitId": str(self.folder_id),
            "Content-Type": "application/json"
        }

        payload = {
            "itemData": {
                "Name": self.queue_name,
                "Priority": "High",
                "SpecificContent": {
                    "To": email_data.get("To"),
                    "Subject": email_data.get("Subject"),
                    "Body": email_data.get("Body")
                   
        }
    }

        }

        response = requests.post(add_item_url, json=payload, headers=headers)

        if response.status_code == 201:
            # Punem 'To' cu literă mare, exact cum e cheia în dicționar
            logging.info(f"✅ Notificare trimisă către {email_data.get('To')}")
            return True
        else:
            logging.error(f"❌ Eroare la adăugare în Queue: {response.status_code}, {response.text}")
            return False


# --- Funcții pentru baza de date ---
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")

def load_db():
    if not os.path.exists(DB_FILE):
        logging.warning(f"[DB] Nu am găsit baza de date la: {DB_FILE}")
        return []
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def validate_record(record):
    required = ["item", "expiry_date", "owner_email", "status"]
    return all(field in record for field in required)


# --- Monitorizare ---
def check_and_alert():
    notifier = NotificationAgent()
    data = load_db()
    updated = False
    
    today = datetime.now().date()
    warning_threshold = 3 # Zile

    logging.info(f"--- [Monitor] Scanare DB la {datetime.now().strftime('%H:%M:%S')} ---")

    for record in data:
        if not validate_record(record):
            logging.warning(f"[Monitor] Record invalid: {record}")
            continue

        if record.get("alert_sent") is True or record.get("status") != "active":
            continue

        try:
            expiry_dt = datetime.strptime(record["expiry_date"], "%Y-%m-%d").date()
            days_left = (expiry_dt - today).days

            if 0 <= days_left <= warning_threshold:
                logging.warning(f"🚨 DETECTAT: {record['item']} expiră în {days_left} zile!")

                alert_payload = {
                    "To": record["owner_email"],
                    "Subject": f"⚠️ BizGenie Alert: {record['item']} expiră curând!",
                    "Body": (
                        f"<h3>Salut,</h3>"
                        f"<p>Agentul de Monitorizare BizGenie a detectat o urgență:</p>"
                        f"<ul>"
                        f"<li><b>Produs/Act:</b> {record['item']}</li>"
                        f"<li><b>Data Expirării:</b> {record['expiry_date']}</li>"
                        f"<li><b>Zile rămase:</b> <span style='color:red; font-weight:bold;'>{days_left}</span></li>"
                        f"</ul>"
                        f"<p>Te rugăm să deschizi aplicația pentru a genera documentele necesare.</p>"
                        f"<hr><small>Generat de BizGenie AI & UiPath Robot</small>"
                    )
                }

                success = notifier.send_alert(alert_payload)

                if success:
                    record["alert_sent"] = True
                    updated = True

        except ValueError:
            logging.error(f"Eroare format dată pentru {record['item']}")

    if updated:
        save_db(data)
        logging.info("[Monitor] Baza de date a fost actualizată (flag-uri alert_sent setate).")


def main():
    logging.info("Monitor pornit.")
    while True:
        check_and_alert()
        time.sleep(30)


if __name__ == "__main__":
    main()
