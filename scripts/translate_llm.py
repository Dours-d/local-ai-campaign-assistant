import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
MODEL = 'llama-3.3-70b-versatile'

def translate(text, source_lang, target_lang):
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY not found in .env")
        return None

    prompt = f"Translate the following text from {source_lang} to {target_lang}. Maintain the profound meaning and respect the terms in parentheses (like Amanah or Shahada) if they are present. Only return the translated text.\n\nText: {text}"

    resp = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {GROQ_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': MODEL,
            'messages': [
                {'role': 'system', 'content': 'You are a professional translator specializing in humanitarian and resilience contexts.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3
        }
    )

    if resp.status_code == 200:
        return resp.json()['choices'][0]['message']['content'].strip()
    else:
        print(f"Error: {resp.status_code} - {resp.text}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python translate_llm.py <text> <source_lang> <target_lang>")
        sys.exit(1)
    
    input_text = sys.argv[1]
    src = sys.argv[2]
    tgt = sys.argv[3]
    
    result = translate(input_text, src, tgt)
    if result:
        print(result)
