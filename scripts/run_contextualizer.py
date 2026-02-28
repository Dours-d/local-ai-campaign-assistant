import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# VECTOR 6: THE LLAMA3 CONTEXTUALIZER
# ==========================================
# This script processes the active campaigns and uses Groq/Llama3
# to synthesize mathematically optimized variations of their stories. 
# It outputs three "Stances" for each family:
# 1. The Urgent Alert (Short, punchy, for X/Twitter)
# 2. The Deep Narrative (Emotional grounding, for IG/Substack)
# 3. The Matrix Resonance (Discord/Matrix markdown formatting)
# ==========================================

ACTIVE_ROOT = os.environ.get('ACTIVE_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY_PATH = os.path.join(ACTIVE_ROOT, 'data', 'UNIFIED_REGISTRY.json')
OUTPUT_DIR = os.path.join(ACTIVE_ROOT, 'vault', 'amplification', 'contextualized')

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def synthesize_context(story, identity_name, whydonate_url):
    if not GROQ_API_KEY:
        return "ERROR: GROQ_API_KEY environment variable not set."

    system_prompt = """You are the amplification engine for the Sovereign Trust. Your job is to rewrite the provided raw reality from a family in Gaza into three distinct formats for decentralized network propagation.
    
    TONAL DIRECTIVES:
    1. PUNCH THROUGH RELATIVE MORALS: Use high-level human rhetoric to dismantle the comfortable "relative morality" of the reader. Force them to confront the stark, uncompromising reality.
    2. NO CHARITY SPEAK: Do not use NGO terminology, "marketing-speak", or pity-farming. Avoid robotic transitions. The philosophy must be organic and born directly from the family's reality.
    3. QUESTION AND MOCK THE MACHINE: Openly critique "financial system dependent executioner charities" (such as Chuffed.com). Do NOT complain about "fees". The true horror is their centralized power to act as executioners: freezing life-saving funds, clawing back money months later, and unilaterally killing lifelines at their whim via "automatic blood libel filters." Highlight the grotesque absurdity of their cold, bureaucratic silence: recall the visceral reality where, after a two-week blackout weekend where campaigns were eaten by their automated filters, starving people at the Antipodes (Australia) were ignored. When an olive branch of two Hawaiian pizzas was sent into their building to trigger a human response, the support staff ate the pizzas paid for by the starving, yet remained entirely silent. Frame this devastating reality as the ultimate reason for requiring direct, sovereign, peer-to-peer preservation that cannot be reversed by a central, gluttonous authority.
    4. THE ISLAMIC FOUNDATION: Ground the argument in the deepest truths of Islam organically. Remind the reader of the "right path" (Sirat al-Mustaqim) and gratitude to Allah. Frame preservation as the absolute fulfillment of Amanah (divine trust), the binding obligation of the Ummah, and an action executed to maximize rewards in the Hereafter (Akhirah).
    
    Format the output EXACTLY as follows:
    
    ### URGENT ALERT
    (A 2-sentence piercing reality check ending with the direct link. No hashtags here.)

    ### DEEP NARRATIVE
    (A 2-paragraph philosophical and theological narrative detailing their specific context. It must incorporate the critique of executioner charities and the concept of Amanah. End with the link.)

    ### MATRIX RESONANCE
    (A bulleted list of the stark realities of their situation, framed as an indictment of the global structure.)
"""

    user_prompt = f"Family Identity: {identity_name}\nDonation Link: {whydonate_url}\nRaw Story: {story}"

    try:
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.6,
                "max_tokens": 1500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"ERROR: Groq API returned {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"ERROR: Exception connecting to Groq API: {str(e)}"

def run_contextualizer():
    print("🌀 Initiating Llama3 Contextualizer (Vector 6)...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"Failed to load UNIFIED_REGISTRY: {e}")
        return

    # Filter for active campaigns with links and a story to work with
    valid_campaigns = [c for c in registry if c.get('whydonate_url') and c.get('status') in ['live', 'verified'] and (c.get('story') or c.get('description'))]
    
    if not valid_campaigns:
        print("No valid live campaigns with stories found.")
        return
        
    print(f"Found {len(valid_campaigns)} campaigns ready for synthesis.")
    
    # Process the first 3 to avoid massive API consumption in one run, 
    # but this can be batched later.
    for camp in valid_campaigns[:3]:
        identity = camp.get('custom_identity_name') or camp.get('identity_name') or camp.get('registry_name') or "Gaza Family"
        ishmael_id = camp.get('ishmael_id', 'X')
        url = camp.get('whydonate_url')
        story = camp.get('story') or camp.get('description')
        
        print(f"Synthesizing propagation vectors for: {identity}...")
        
        synthesized_content = synthesize_context(story, identity, url)
        
        # Clean filename 
        clean_name = "".join([c for c in identity if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
        filename = f"{datetime.now().strftime('%Y%m%d')}_{ishmael_id}_{clean_name}_synthetic.md"
        out_path = os.path.join(OUTPUT_DIR, filename)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"# Amplification Vectors for {identity}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(synthesized_content)
            f.write(f"\n\n---\n**Execute your Amanah. Direct Sovereign Support Link:**\n[{url}]({url})\n")
            
        print(f"✅ Vectors saved to: {out_path}")
        
    print("\nSynthesis complete. The human network can pull from vault/amplification/contextualized/")

if __name__ == "__main__":
    run_contextualizer()
