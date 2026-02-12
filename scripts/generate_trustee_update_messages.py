
import json
import os
import datetime
import sys

# Sibling import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import generate_debt_table as debt_source

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
LEDGER_FILE = os.path.join(DATA_DIR, 'internal_ledger.json')
REGISTRY_FILE = os.path.join(DATA_DIR, 'campaign_registry.json')
INDIVIDUAL_INDEX = os.path.join(DATA_DIR, 'reports', 'individual', 'index.json')
OUTBOX_DIR = os.path.join(DATA_DIR, 'trustee_updates')

UNIFIED_PIONEER_NAME = "Olive of Gaza (Mahmoud & Reem)"
UNIFIED_PIONEER_KEYS = {
    "Mahmoud-001", "Mahmoud-002", "Mahmoud-003", "Mahmoud-004", "Mahmod-002",
    "Reem-002", "Reems-001", "Reems-003", "Reems-004", "Reems-005", "Reems-006",
    "Mahmoud Basem Alkfarna", "Mahmoud Basem", "Olive of Gaza (Zaytun)"
}
SAMIRA_UNIFIED_NAME = "Samirah"
SAMIRA_KEYS = {"Samira", "Samirah"}

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def get_status_label(portion, solidarity):
    if portion > 1000: return "✊ Pioneer"
    if solidarity > 0.01: return "🛡️ Solidary Pillar"
    if solidarity < -0.01: return "🌾 Sustained"
    return "📝 Trustee"

def generate_update_messages():
    ledger = load_json(LEDGER_FILE)
    registry = load_json(REGISTRY_FILE).get("mappings", {})
    individual_index = load_json(INDIVIDUAL_INDEX)
    debts_list = debt_source.get_all_debts()
    
    os.makedirs(OUTBOX_DIR, exist_ok=True)

    entities = {}

    def get_final_name(raw_name):
        if raw_name in UNIFIED_PIONEER_KEYS: return UNIFIED_PIONEER_NAME
        if raw_name in SAMIRA_KEYS: return SAMIRA_UNIFIED_NAME
        return raw_name

    # Step 1: Ingest Ledger
    for name, data in ledger.items():
        fname = get_final_name(name)
        if fname not in entities: entities[fname] = {"raised": 0.0, "portion": 0.0, "original_names": set()}
        entities[fname]["raised"] += data.get('raised_gross_eur', 0)
        entities[fname]["original_names"].add(name)

    # Step 2: Ingest Debts
    mapped_hints = set()
    for item in debts_list:
        hint = item['hint']
        fname = get_final_name(hint)
        
        # Fuzzy matching check for unification
        if fname == hint:
            for k in UNIFIED_PIONEER_KEYS:
                if k.lower() in hint.lower(): fname = UNIFIED_PIONEER_NAME; break
            if fname == hint:
                for k in SAMIRA_KEYS:
                    if k.lower() in hint.lower(): fname = SAMIRA_UNIFIED_NAME; break

        if fname not in entities: entities[fname] = {"raised": 0.0, "portion": 0.0, "original_names": set()}
        
        if hint not in mapped_hints:
            entities[fname]["portion"] += item['amount']
            entities[fname]["original_names"].add(hint)
            mapped_hints.add(hint)

    # Step 3: Special Cases (Sync with generate_trust_report.py)
    if UNIFIED_PIONEER_NAME in entities:
        entities[UNIFIED_PIONEER_NAME]["portion"] = max(entities[UNIFIED_PIONEER_NAME]["portion"], 3494.53)
    if SAMIRA_UNIFIED_NAME in entities:
        if abs(entities[SAMIRA_UNIFIED_NAME]["portion"] - 811.14) < 0.01:
            entities[SAMIRA_UNIFIED_NAME]["portion"] = 405.57

    # Step 4: Map back to WhatsApp for communication
    name_to_whatsapp = {}
    
    # Use individual index for best mapping
    for entry in individual_index:
        b_name = entry.get("beneficiary")
        wa = entry.get("whatsapp")
        if b_name and wa and wa != "Unknown":
            name_to_whatsapp[b_name] = wa
            
    # Fallback to Registry
    for r_id, r_data in registry.items():
        r_name = r_data.get("name")
        wa = r_data.get("whatsapp")
        if r_name and wa and wa != "Unknown" and r_name not in name_to_whatsapp:
            name_to_whatsapp[r_name] = wa

    count = 0
    for fname, data in entities.items():
        if data["raised"] < 0.01 and data["portion"] < 0.01: continue
        
        solidarity = data["raised"] - data["portion"]
        status = get_status_label(data["portion"], solidarity)
        
        # Find WhatsApp
        whatsapp = name_to_whatsapp.get(fname)
        if not whatsapp:
            # Try original names
            for oname in data["original_names"]:
                if oname in name_to_whatsapp:
                    whatsapp = name_to_whatsapp[oname]
                    break
        
        if not whatsapp: continue # Cannot communicate without WA

        # --- Message Template ---
        msg = f"السلام عليكم ورحمة الله وبركاته، يا **{fname}**.\n\n"
        msg += f"نُحييك على ثباتك وجهدك. نود أن نطلعك على وضعك الحالي ضمن **صندوق التكافل السيادي (Sovereign Trust)**:\n\n"
        msg += f"🏅 دورك الحالي: **{status}**\n"
        msg += f"📊 مجهودك في جمع التبرعات: €{data['raised']:,.2f}\n"
        
        if solidarity >= 0:
            msg += f"🤝 مساهمتك التضامنية: €{solidarity:,.2f} (فائض)\n"
            msg += f"نحن نُقدّر بعمق أن جهودك الفائضة هي ما يسمح للآخرين في الصندوق بالبقاء والاستمرار، وهو ميثاق التكافل الذي اخترناه.\n\n"
        else:
            msg += f"⚠️ الفجوة المتبقية: €{abs(solidarity):,.2f}\n"
            msg += f"نحن نعمل معاً لتغطية هذه الفجوة من خلال مجهود المجموعة. ثباتكم هو جزء من قوتنا الجماعية.\n\n"

        msg += f"📜 **تقرير صحة الصندوق الموحد**:\n"
        msg += f"يمكنك الاطلاع على التقرير الكامل والشفافية التامة عبر الرابط التالي:\n"
        msg += f"https://dours-d.github.io/local_ai_campaign_assistant/data/reports/trust_health_report.md\n\n"
        
        msg += f"شكرًا لكونك جزءًا من هذا الميثاق الجماعي للبقاء.\n"
        msg += f"--- \n"
        msg += f"Salam Alaykum, **{fname}**.\n\n"
        msg += f"We honor your effort. Here is your current status within the **Sovereign Trust**:\n\n"
        msg += f"🏅 Your Role: **{status}**\n"
        msg += f"📊 Fundraising Effort: €{data['raised']:,.2f}\n"
        
        if solidarity >= 0:
            msg += f"🤝 Solidarity Contribution: €{solidarity:,.2f} (Surplus)\n"
            msg += f"We deeply honor that your surplus effort is what permits others in the Trust to survive. This is the pact of solidarity we carry together.\n\n"
        else:
            msg += f"⚠️ Remaining Gap: €{abs(solidarity):,.2f}\n"
            msg += f"We are working together to close this gap through collective effort. Your resilience is part of our shared strength.\n\n"
            
        msg += f"🔗 **Full Trust Health Report**:\n"
        msg += f"View the transparent collective report here:\n"
        msg += f"https://dours-d.github.io/local_ai_campaign_assistant/data/reports/trust_health_report.md\n\n"
        
        msg += f"Thank you for being part of this shared survival pact."

        filename = f"{whatsapp.replace('+', '').replace(' ', '')}_update.txt"
        with open(os.path.join(OUTBOX_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(msg)
        count += 1

    print(f"Generated {count} trustee update messages in {OUTBOX_DIR}")

if __name__ == "__main__":
    generate_update_messages()
