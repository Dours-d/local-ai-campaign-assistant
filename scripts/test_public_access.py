
import requests
import json

def test_public_chat():
    url = "http://127.0.0.1:5000/api/chat"
    payload = {
        "query": "Hello Noor, are you open to the public?",
        "mode": "local"
    }
    
    try:
        print(f"Testing Public Chat Access: {url}")
        # No headers, no auth
        res = requests.post(url, json=payload, timeout=10)
        
        print(f"Status Code: {res.status_code}")
        if res.ok:
            print("Response:", res.json())
            print("SUCCESS: Public access verified.")
        else:
            print("Error:", res.text)
            print("FAILURE: Access denied or error.")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_public_chat()
