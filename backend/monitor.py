import requests
import logging

class NotificationAgent:
    def __init__(self):
        # Endpoint corect pentru generare token
        self.token_url = "https://cloud.uipath.com/identity_/connect/token"

        # Endpoint corect pentru Orchestrator
        self.base_url = "https://cloud.uipath.com/persobzhsnqq/DefaultTenant/orchestrator_/odata"

        # 🔑 Cheile sunt păstrate direct în cod
        self.client_id = "c80c3a63-58e2-426a-bf39-7db77c23b4af"
        self.client_secret = "EGUdBHEei$UVwVQ?J#A(H7W8n3@@bTslv~%0k@~ipNsYU0CF4$455y3yLySR@~B?"

        self.folder_id = 6870187
        self.queue_name = "AlertsQueue"

    def _get_access_token(self):
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "OR.Queues.Write"
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
                    "email": email_data.get("to"),
                    "subject": email_data.get("subject"),
                    "body": email_data.get("body")
                }
            }
        }

        response = requests.post(add_item_url, json=payload, headers=headers)

        if response.status_code == 201:
            logging.info(f"✅ Notificare trimisă către {email_data.get('to')}")
            return True
        else:
            logging.error(f"❌ Eroare la adăugare în Queue: {response.status_code}, {response.text}")
            return False
