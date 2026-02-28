import os
import json
import requests
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# VECTOR 12: THE MASTER WEAVER (LONG-FORM RHETORIC)
# ==========================================
# This script extracts campaign data and feeds it into Llama3
# (via Groq API) to synthesize long-form, high-level rhetoric 
# essays designed for Medium/Substack.
#
# TONAL DIRECTIVE: The output must actively punch through the 
# "common sense of human relative morals." It must avoid NGO 
# marketing speech and instead rely on philosophical weight, 
# stark reality, and the uncompromising sovereignty of human life.
# ==========================================

ACTIVE_ROOT = os.environ.get('ACTIVE_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY_PATH = os.path.join(ACTIVE_ROOT, 'data', 'UNIFIED_REGISTRY.json')
OUTPUT_DIR = os.path.join(ACTIVE_ROOT, 'vault', 'amplification', 'longform')

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def synthesize_longform(campaign_data):
    """Feeds campaign data to Llama3 to generate a deep, rhetorical essay."""
    
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY environment variable is not set. Cannot synthesize.")
        return None
        
    identity = campaign_data.get('custom_identity_name') or campaign_data.get('identity_name') or campaign_data.get('registry_name') or "Unknown Family"
    story = campaign_data.get('story', 'No story provided.')
    goal = campaign_data.get('goal', 'Unknown')
    link = campaign_data.get('whydonate_url', '#')
    image_url = campaign_data.get('image', '')
    
    # We construct a prompt that forces the specific rhetorical style requested by the user
    system_prompt = """You are the 'Master Weaver' for the Sovereign Trust. Your objective is to write a long-form essay (approx 1000 words) based on the provided human reality. 
    
CRITICAL TONAL DIRECTIVES:
1. PUNCH THROUGH RELATIVE MORALS: You must use high-level human rhetoric to dismantle the comfortable "relative morality" of the reader. Force them to confront the stark, uncompromising reality of survival and sovereignty. Do not write like an academic; write like a prophet addressing a sleeping world.
2. NO CHARITY SPEAK & NO CLICHES: Do not use NGO terminology, "marketing-speak", or pity-farming. Avoid robotic transitions and generic philosophical quotes. The philosophy must be organic and born directly from the family's reality.
3. WEAPONIZED PHILOSOPHY: Frame the family's situation as an indictment of the current global structure. 
4. QUESTION AND MOCK THE MACHINE: Openly critique "financial system dependent executioner charities" (such as Chuffed.com). Do NOT complain about mundane "fees". The true horror is their centralized power to act as executioners: freezing life-saving funds, clawing back money months later, and unilaterally killing lifelines at their whim via "automatic blood libel filters." Highlight the grotesque absurdity of their cold, bureaucratic silence: recall the visceral reality where, after a two-week blackout weekend where campaigns were eaten by their automated filters, starving people at the Antipodes (Australia) were ignored. When an olive branch of two Hawaiian pizzas was sent into their building to trigger a human response, the support staff ate the pizzas paid for by the starving, yet remained entirely silent. Frame this devastating reality as the ultimate reason for requiring direct, sovereign, peer-to-peer preservation that cannot be reversed by a central, gluttonous authority. Integrate this critique naturally.
5. THE ISLAMIC FOUNDATION: Ground the argument in the deepest truths of Islam without sounding like a standard khutbah. Remind yourselves and the reader to be grateful to Allah Subhanahu wa Ta'ala. Remind the reader of the "right path" (Sirat al-Mustaqim). Frame the act of direct preservation not as optional charity, but as the absolute fulfillment of Amanah (divine trust), the binding obligation of the Ummah, and an action executed with the sole objective of maximizing our rewards in the Hereafter (Akhirah).
6. THE FORMAT: Use Markdown. Give it a powerful, piercing title. Structure it as a single, flowing, devastating essay.
7. THE CALL: Embed the provided direct support link naturally at the end. Do not beg. State it as the singular mechanism for the reader to sever ties with complacency and execute their Amanah."""

    user_prompt = f"""
Family Identity: {identity}
Financial Target: €{goal}
Direct Link: {link}

Raw Reality (The ground truth):
{story}

Synthesize the Long-Form Archive entry for this reality following the tonal directives. It must read like a profound, challenging essay."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile", # Using the 70B model for high-level reasoning and prose
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 3000
    }
    
    print(f"Dialing Llama3 API for high-level rhetorical synthesis of {identity}...")
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"API Error during synthesis: {e}")
        if hasattr(e, 'response') and getattr(e, 'response') is not None:
            print(f"Groq API Response: {e.response.text}")
        return None
    except KeyError:
        print("Unexpected API response structure.")
        return None

def main():
    print("🌀 Initiating Vector 12: The Master Weaver (Long-Form Synthesis)...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
        
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"Failed to load UNIFIED_REGISTRY: {e}")
        return

    # Filter for campaigns that have enough data to warrant a long-form essay
    valid_campaigns = [c for c in registry if c.get('story') and len(c.get('story')) > 50 and c.get('status') in ['live', 'verified']]
    
    if not valid_campaigns:
        print("No valid campaigns with sufficient ground truth found for long-form synthesis.")
        return
        
    print(f"Found {len(valid_campaigns)} campaigns ready for deep rhetorical synthesis.")
    
    # Process just the first 2 to save tokens/time on initial batch runs
    for camp in valid_campaigns[:2]:
        identity = camp.get('custom_identity_name') or camp.get('identity_name') or camp.get('registry_name') or "Unknown"
        ishmael_id = camp.get('ishmael_id', 'X')
        
        essay_content = synthesize_longform(camp)
        
        if essay_content:
            # We inject the image at the top of the markdown if it exists
            image_url = camp.get('image', '')
            if image_url:
                essay_content = f"![{identity}]({image_url})\n\n" + essay_content
                
            clean_name = "".join([c for c in identity if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"{date_str}_{ishmael_id}_{clean_name}_longform.md"
            out_path = os.path.join(OUTPUT_DIR, filename)
            
            # Hardcode the essential call to action to guarantee the link is always present
            link = camp.get('whydonate_url', '#')
            essay_content += f"\n\n---\n**Execute your Amanah. Direct Sovereign Support Link:**\n[{link}]({link})\n"
            
            with open(out_path, 'w', encoding='utf-8') as mf:
                mf.write(essay_content)
                
            print(f"✅ Long-Form Essay synthesized and archived: {out_path}")
            
    print("\nVector 12 Synthesis complete. Essays are available in the vault for Medium injection.")

if __name__ == "__main__":
    main()
