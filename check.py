import os, requests
from dotenv import load_dotenv
load_dotenv()
key=os.getenv('GROQ_API_KEY')
print(f'Key: {key[:10]}...')
try:
    resp=requests.post('https://api.groq.com/openai/v1/chat/completions', 
                       headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}, 
                       json={'model': 'llama-3.3-70b-versatile', 'messages': [{'role': 'user', 'content': 'Hi'}], 'max_tokens': 10})
    print(f'Status: {resp.status_code}')
    print(resp.text)
except Exception as e:
    print(e)
