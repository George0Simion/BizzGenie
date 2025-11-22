#!/usr/bin/env python3
import sys
import json
import requests

URL = "http://127.0.0.1:5001/text"

def main():
    # Read everything from stdin
    raw_input = input()

    if not raw_input:
        print("No input received on stdin.")
        return

    print("Sending to URL:", URL)
    # Build JSON payload
    payload = {
        "msg": raw_input
    }

    try:
        resp = requests.post(URL, json=payload, timeout=5)
        print("Status:", resp.status_code)
        print("Response:", resp.json())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
