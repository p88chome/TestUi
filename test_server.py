import requests
import json

try:
    print("Testing connection to http://127.0.0.1:8001/api/v1/agent/run ...")
    response = requests.post(
        "http://127.0.0.1:8001/api/v1/agent/run",
        json={"query": "hello"},
        timeout=5
    )
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)
except Exception as e:
    print(f"Connection Failed: {e}")
