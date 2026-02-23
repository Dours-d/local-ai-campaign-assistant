import json
import re
import os

md_path = r'c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\data\final_real_growth_list.md'
json_path = r'c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\data\final_real_growth_list.json'

def get_verified_from_md():
    verified = []
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_verified = False
    for line in lines:
        if '## ✅ Verified' in line:
            in_verified = True
            continue
        if '## ❌ Dropped' in line:
            in_verified = False
            continue
        
        if in_verified and '|' in line and 'WhatsApp' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                wa = parts[1]
                bid = parts[2]
                title_raw = parts[3]
                source = parts[4]
                
                # Extract title from markdown link if present
                title_match = re.search(r'\[(.*?)\]', title_raw)
                title = title_match.group(1) if title_match else title_raw
                
                verified.append({
                    "whatsapp": wa,
                    "bid": bid,
                    "title": title,
                    "source": source
                })
    return verified

def sync_json():
    with open(json_path, 'r', encoding='utf-8') as f:
        # Try to load existing, but if it has my lint error, we might need to fix it
        content = f.read()
        # Fix my double brace error if it exists
        content = content.replace('    }\n},', '    },')
        try:
            data = json.loads(content)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            # Minimal fix for common duplicate brace from my previous turn
            content = content.replace('    }\n},', '    },')
            data = json.loads(content)

    md_verified = get_verified_from_md()
    
    existing_bids = {item['bid'] for item in data}
    
    new_entries = 0
    for mv in md_verified:
        # Skip entries that are just placeholders like "sub_..." if they already exist
        if mv['bid'] not in existing_bids:
            data.append({
                "bid": mv['bid'],
                "description": "",
                "goal": 5000,
                "identity_indices": [0, 1],
                "status": "verified",
                "title": mv['title'],
                "validation_source": mv['source'],
                "whatsapp": mv['whatsapp']
            })
            existing_bids.add(mv['bid'])
            new_entries += 1

    # Now add the 14 recovered leads (they should be in get_verified_from_md if I already added them to .md)
    # But wait, I might not have successfully added them to .md yet if my previous tool call failed!
    # I'll manually add them to the data list just in case.
    
    recovered_leads = [
        {"bid": "chuffed_129480", "wa": "972598832400", "title": "Help Ahmed and his family survive the genocide of Gaza, Palestine."},
        {"bid": "chuffed_129858", "wa": "972598568294", "title": "Help Ahmed and his family rebuild their lives out of Gaza, Palestine."},
        {"bid": "chuffed_130195", "wa": "970599157072", "title": "Help Marah and her family rebuild their lives, Palestine."},
        {"bid": "chuffed_131077", "wa": "972567685300", "title": "Help Umm Iman and Her family survive the genocide in Gaza, Palestine."},
        {"bid": "chuffed_131837", "wa": "970599904464", "title": "Help Yasmine and Her family to rebuild their life in Gaza, Palestine."},
        {"bid": "chuffed_131857", "wa": "972597014703", "title": "Save Salman Ali and his family from the awful destruction in Gaza, Palestine."},
        {"bid": "chuffed_149509", "wa": "972599810762", "title": "Help Umm Masoud and her daughter, survivors of the rubbles of Gaza"},
        {"bid": "chuffed_149833", "wa": "970597043580", "title": "Help Mohammed's family rebuild their future and safety"},
        {"bid": "chuffed_149915", "wa": "972594847782", "title": "Help Abdullah Mohammed support his 7 sons & daughters in Gaza"},
        {"bid": "chuffed_150060", "wa": "972598669093", "title": "Help Akram and his family continue despite the pain in Gaza"},
        {"bid": "chuffed_150453", "wa": "972599084394", "title": "Help Abu Muhammad feed his nine young children in Gaza"},
        {"bid": "chuffed_151509", "wa": "972599654484", "title": "Help Heba saving her family from the winter's nightmares in Gaza"},
        {"bid": "chuffed_151590", "wa": "972594837798", "title": "Help Umm Sami and her family surpass the winter conditions in Gaza"},
        {"bid": "chuffed_152352", "wa": "972593949632", "title": "Help Abu Haytham to provide his four children in Gaza"}
    ]
    
    for rl in recovered_leads:
        if rl['bid'] not in existing_bids:
            data.append({
                "bid": rl['bid'],
                "description": "",
                "goal": 5000,
                "identity_indices": [0, 1],
                "status": "verified",
                "title": rl['title'],
                "validation_source": "missing_anchor_recovered",
                "whatsapp": rl['wa']
            })
            existing_bids.add(rl['bid'])
            new_entries += 1

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Sync complete. Added {new_entries} new entries. Total: {len(data)}")

if __name__ == "__main__":
    sync_json()
