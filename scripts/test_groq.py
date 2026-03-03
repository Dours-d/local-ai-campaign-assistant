import os
import requests
from dotenv import load_dotenv

load_dotenv()
groq_key = os.getenv('GROQ_API_KEY')
print(f"Key present: {bool(groq_key)}")
if groq_key:
    print(f"Key starts with: {groq_key[:10]}...")
    print(f"Key length: {len(groq_key)}")

resp = requests.post(
    'https://api.groq.com/openai/v1/chat/completions',
    headers={'Authorization': f'Bearer {groq_key}', 'Content-Type': 'application/json'},
    json={
        'model': 'llama-3.3-70b-versatile',
        'messages': [{'role': 'user', 'content': 'Hello'}],
        'max_tokens': 10
    }
)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
