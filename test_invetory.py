import requests

URL = "http://localhost:5002/inventory"   # change to your inventory service port

def test_get_inventory():
    try:
        response = requests.get(URL, timeout=5)
        print("Status:", response.status_code)
        print("Response:")
        print(response.json())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_get_inventory()
