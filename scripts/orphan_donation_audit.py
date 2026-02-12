import json
import csv
import re
import os
import sys
import glob
import html

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DATA_DIR = 'data'
XML_PATH = 'temp_total2/content.xml'
OUTPUT_CSV = os.path.join(DATA_DIR, 'reports', 'orphan_donations_with_whatsapp.csv')
MANUAL_MAPPINGS_FILE = os.path.join(DATA_DIR, 'user_manual_couplings.json')
REGISTRY_FILE = os.path.join(DATA_DIR, 'campaign_registry.json')

import unicodedata

def cleanup_match_key(text):
    if not text: return ""
    text = html.unescape(text)
    text = text.replace("<text:s/>", " ")
    # Normalize unicode accents for Latin chars but keep the base characters and Arabic
    text = "".join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    # Strip emojis and symbols - keep alphanumeric and Arabic
    clean = re.sub(r'[^\s\w\u0600-\u06FF]', '', text)
    # Normalize spaces and lower case
    clean = " ".join(clean.lower().split())
    # Remove common stop words for matching
    for stop in ["help", "save"]:
        if clean.startswith(stop + " "):
            clean = clean[len(stop)+1:].strip()
    return clean

def build_phone_mapping():
    """Builds a comprehensive mapping from multiple sources."""
    mapping = {}
    
    def add_to_mapping(key, phone):
        if not key or not phone: return
        clean = cleanup_match_key(key)
        if clean:
            mapping[clean] = phone
        # Also keep raw lowercase for safety
        mapping[key.lower().strip()] = phone

    # 1. Load manual mappings from user (highest priority)
    if os.path.exists(MANUAL_MAPPINGS_FILE):
        with open(MANUAL_MAPPINGS_FILE, 'r', encoding='utf-8') as f:
            manual = json.load(f)
            for title, phone in manual.items():
                add_to_mapping(title, phone)

    # 2. Load unified campaigns
    unified_path = os.path.join(DATA_DIR, 'campaigns_unified.json')
    if os.path.exists(unified_path):
        with open(unified_path, 'r', encoding='utf-8') as f:
            unified = json.load(f)
            for camp in unified.get('campaigns', []):
                title = camp.get('title')
                phone = camp.get('whatsapp_chat_id')
                add_to_mapping(title, phone)
                
                internal_name = camp.get('privacy', {}).get('internal_name')
                add_to_mapping(internal_name, phone)

    # 3. Load campaign registry
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            registry = json.load(f)
            for reg_id, info in registry.get('mappings', {}).items():
                name = info.get('name')
                phone = info.get('whatsapp') or reg_id
                add_to_mapping(name, phone)
                add_to_mapping(reg_id, phone)

    # 4. Load onboarding submissions
    submission_files = glob.glob(os.path.join(DATA_DIR, 'onboarding_submissions', '*.json'))
    for sf in submission_files:
        try:
            with open(sf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                phone = data.get('whatsapp_number') or data.get('beneficiary_id', '').replace('viral_+', '').replace('+', '').strip()
                if not phone: continue
                
                title = data.get('title')
                add_to_mapping(title, phone)
                # Slug match
                if title:
                    slug_match = re.search(r'project/(\d+)-(.*)', title)
                    if slug_match:
                        add_to_mapping(slug_match.group(2).replace('-', ' '), phone)
                
                display_name = data.get('display_name')
                add_to_mapping(display_name, phone)
        except:
            continue
            
    return mapping

def extract_rows_fast(xml_data, sheet_name):
    """Efficiently extract all rows for a given sheet."""
    names_to_try = [sheet_name, sheet_name.replace("'", "&apos;")]
    sheet_xml = None
    for name in names_to_try:
        match = re.search(f'table:name="{name}"', xml_data)
        if match:
            start = match.start()
            end = xml_data.find('</table:table>', start)
            sheet_xml = xml_data[start:end]
            break
    
    if not sheet_xml: return []
    
    rows = []
    row_pattern = re.compile(r'<table:table-row.*?>(.*?)</table:table-row>', re.DOTALL)
    cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell).*?(/|>(.*?)</\1)>', re.DOTALL)
    
    for r_idx, r_match in enumerate(row_pattern.finditer(sheet_xml)):
        if r_idx == 0: continue # Skip header
        
        row_content = r_match.group(1)
        curr_col = 0
        row_data = {}
        for c_match in cell_pattern.finditer(row_content):
            cell_xml = c_match.group(0)
            rep_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
            rep_count = int(rep_match.group(1)) if rep_match else 1
            
            val = ""
            v_match = re.search(r'office:value="([^"]*)"', cell_xml)
            if v_match: val = v_match.group(1)
            else:
                p_match = re.search(r'<text:p>(.*?)</text:p>', cell_xml)
                if p_match: val = p_match.group(1)
            
            if val.strip():
                row_data[curr_col] = val.strip()
            
            curr_col += rep_count
            if curr_col > 60: break # Column limits
            
        if row_data:
            rows.append(row_data)
    return rows

def run_audit():
    if not os.path.exists(XML_PATH):
        print(f"Error: {XML_PATH} not found.")
        return

    xml_data = open(XML_PATH, 'r', encoding='utf-8', errors='ignore').read()
    phone_map = build_phone_mapping()
    
    sheets = ['noor', 'Rania', 'Mohammed  Suhail', 'Ibtisam', 'Fayez', 
              "Let's draw a smile (Ahmed's daughter)", 'Amani', 'Zina', 'Hala', 'Samirah', 'Mahmoud Basem']

    all_events = []
    
    for sheet_name in sheets:
        print(f"Processing sheet: {sheet_name}...")
        rows = extract_rows_fast(xml_data, sheet_name)
        
        for data in rows:
            title = data.get(0, '').strip()
            if not title: title = data.get(1, '').strip()
            
            amt_str = str(data.get(4, '0')).replace(',', '')
            try:
                amt = float(amt_str)
            except:
                amt = 0.0
                
            if amt <= 0 and not title: continue
            
            phone = "Unmapped"
            clean_title = cleanup_match_key(title)
            clean_sheet = cleanup_match_key(sheet_name)
            
            # Cascading match
            if clean_title in phone_map:
                phone = phone_map[clean_title]
            elif title.lower() in phone_map:
                phone = phone_map[title.lower()]
            elif clean_sheet in phone_map:
                phone = phone_map[clean_sheet]
            else:
                # Heuristics for specific names mentioned by user
                if "fares" in clean_title: phone = "970592892385"
                elif "mahmoud" in clean_title: phone = phone_map.get("mahmoud basem", "Unmapped")
                elif "rania" in clean_title: phone = phone_map.get("rania", "Unmapped")
                elif "fayez" in clean_title: phone = phone_map.get("fayez", "Unmapped")
                elif "suhail" in clean_title: phone = phone_map.get("suhail", "972594116562")
                elif "bilal" in clean_title: phone = phone_map.get("bilal", "972592487035")
            
            all_events.append({
                "Sheet": sheet_name,
                "Campaign Title": html.unescape(title),
                "Amount (EUR)": f"{amt:.2f}",
                "WhatsApp Phone": phone
            })

    # Output CSV
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Sheet", "Campaign Title", "Amount (EUR)", "WhatsApp Phone"])
        writer.writeheader()
        writer.writerows(all_events)
        
    mapped_count = sum(1 for e in all_events if e["WhatsApp Phone"] != "Unmapped")
    print(f"\nAudit completed.")
    print(f"- Total events: {len(all_events)}")
    print(f"- Mapped: {mapped_count}")
    print(f"- Unmapped: {len(all_events) - mapped_count}")
    print(f"- Final data saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    run_audit()
