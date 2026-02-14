
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key present: {bool(api_key)}")

if api_key:
    if len(api_key) > 5:
        print(f"API Key start: {api_key[:5]}...")
    
    try:
        print("Attempting connection to Groq...")
        res = requests.post('https://api.groq.com/openai/v1/chat/completions', 
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "user", "content": "Hello, are you online?"}
                ],
                "stream": False
            }, timeout=15)
        
        print(f"Status Code: {res.status_code}")
        if res.ok:
            print("Response:", res.json())
        else:
            print("Error Response:", res.text)
    except Exception as e:
        print(f"Exception: {e}")
else:
    print("No API Key found in env.")
