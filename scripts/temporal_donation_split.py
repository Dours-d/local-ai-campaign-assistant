import json
import csv
import re
import os
import sys
import html
from datetime import datetime
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.orphan_donation_audit import build_phone_mapping, cleanup_match_key

# Threshhold for temporal split
THRESHOLD_DATE = datetime(2025, 10, 31)

DATA_DIR = 'data'
TOTAL2_XML = 'temp_total2/content.xml'
DAILY_XML = 'temp_daily/content.xml'
TOTAL2_STYLES = 'temp_total2/styles.xml'
DAILY_STYLES = 'temp_daily/styles.xml'

def is_paid_color(hex_color):
    if not hex_color or not hex_color.startswith('#'): return False
    hex_color = hex_color.lower()
    # Explicit green hits from user/analysis
    if hex_color in ['#ccffcc', '#d4ea6b', '#e8f2a1', '#99ff99']:
        return True
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        # Green dominance check for lighter greens
        return g > r and g > b and g > 200
    except:
        return False

def get_paid_styles(styles_xml_path, content_xml_path):
    """Identifies style names that indicate a paid status."""
    paid_styles = set(['Good'])
    
    def extract_from_file(path):
        if not os.path.exists(path): return
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            xml = f.read()
        blocks = re.findall(r'<style:style style:name="([^"]+)"[^>]*>(.*?)</style:style>', xml, re.DOTALL)
        for name, content in blocks:
            color_match = re.search(r'fo:background-color="([^"]+)"', content)
            if color_match and is_paid_color(color_match.group(1)):
                paid_styles.add(name)
                
    extract_from_file(styles_xml_path)
    extract_from_file(content_xml_path)
    return paid_styles

def extract_rows_with_status(xml_data, sheet_name, paid_styles):
    """Extracts rows and determines 'Paid' status based on cell styles."""
    match = re.search(f'table:name="{sheet_name}"', xml_data)
    if not match: return []
    
    start = match.start()
    end = xml_data.find('</table:table>', start)
    sheet_xml = xml_data[start:end]
    
    rows = []
    row_pattern = re.compile(r'<table:table-row.*?>(.*?)</table:table-row>', re.DOTALL)
    cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell).*?(/|>(.*?)</\1)>', re.DOTALL)
    
    for r_idx, r_match in enumerate(row_pattern.finditer(sheet_xml)):
        if r_idx == 0: continue # Skip header
        
        row_content = r_match.group(1)
        curr_col = 0
        row_data = {}
        is_paid = False
        
        for c_match in cell_pattern.finditer(row_content):
            cell_xml = c_match.group(0)
            
            # Extract style
            style_match = re.search(r'table:style-name="([^"]+)"', cell_xml)
            style_name = style_match.group(1) if style_match else None
            
            if style_name in paid_styles:
                is_paid = True
            
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
            if curr_col > 60: break
            
        if row_data:
            row_data['is_paid'] = is_paid
            rows.append(row_data)
    return rows

def parse_ods_date(date_str):
    if not date_str: return None
    # Formats seen: '2025-10-29 03:09:36', '2025-10-28T16:09'
    date_str = date_str.replace('T', ' ')
    try:
        return datetime.strptime(date_str[:16], '%Y-%m-%d %H:%M')
    except:
        return None

def run_split_audit():
    phone_map = build_phone_mapping()
    
    # Load styles
    paid_styles_total2 = get_paid_styles(TOTAL2_STYLES, TOTAL2_XML)
    paid_styles_daily = get_paid_styles(DAILY_STYLES, DAILY_XML)
    
    pre_31_unpaid = []
    post_31_all = []
    
    # 1. Process Total2.ods (Legacy)
    if os.path.exists(TOTAL2_XML):
        xml = open(TOTAL2_XML, 'r', encoding='utf-8', errors='ignore').read()
        sheets = ['noor', 'Rania', 'Mohammed  Suhail', 'Ibtisam', 'Fayez', 'Amani', 'Zina', 'Hala', 'Samirah', 'Mahmoud Basem']
        for s in sheets:
            rows = extract_rows_with_status(xml, s, paid_styles_total2)
            for r in rows:
                ts = parse_ods_date(r.get(11))
                title = r.get(0) or r.get(1, "Unknown")
                amt = r.get(4, "0")
                phone = phone_map.get(cleanup_match_key(title), "Unmapped")
                
                event = {
                    "Timestamp": str(ts) if ts else "N/A",
                    "Campaign": html.unescape(title),
                    "Amount": amt,
                    "Status": "Paid" if r['is_paid'] else "Unpaid",
                    "WhatsApp": phone,
                    "Source": f"Total2:{s}"
                }
                
                if ts and ts < THRESHOLD_DATE:
                    if not r['is_paid']:
                        pre_31_unpaid.append(event)
                elif ts and ts >= THRESHOLD_DATE:
                    post_31_all.append(event)

    # 2. Process Daily.ods (Payments)
    if os.path.exists(DAILY_XML):
        xml = open(DAILY_XML, 'r', encoding='utf-8', errors='ignore').read()
        rows = extract_rows_with_status(xml, 'Payments', paid_styles_daily)
        for r in rows:
            ts = parse_ods_date(r.get(11))
            title = r.get(0) or r.get(1, "Unknown")
            amt = r.get(4, "0")
            phone = phone_map.get(cleanup_match_key(title), "Unmapped")
            
            event = {
                "Timestamp": str(ts) if ts else "N/A",
                "Campaign": html.unescape(title),
                "Amount": amt,
                "Status": "Paid" if r['is_paid'] else "Unpaid",
                "WhatsApp": phone,
                "Source": "Daily:Payments"
            }
            
            if ts and ts >= THRESHOLD_DATE:
                post_31_all.append(event)
            elif ts and ts < THRESHOLD_DATE and not r['is_paid']:
                pre_31_unpaid.append(event)

    # Write Reports
    os.makedirs(os.path.join(DATA_DIR, 'reports'), exist_ok=True)
    
    with open(os.path.join(DATA_DIR, 'reports', 'pre_oct31_unpaid_investigation.csv'), 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Timestamp", "Campaign", "Amount", "Status", "WhatsApp", "Source"])
        writer.writeheader()
        writer.writerows(pre_31_unpaid)
        
    with open(os.path.join(DATA_DIR, 'reports', 'post_oct31_daily_audit.csv'), 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Timestamp", "Campaign", "Amount", "Status", "WhatsApp", "Source"])
        writer.writeheader()
        writer.writerows(post_31_all)
        
    print(f"Audit Complete.")
    print(f"- Pre-31/10 Unpaid identified: {len(pre_31_unpaid)}")
    print(f"- Post-31/10 Daily events processed: {len(post_31_all)}")

if __name__ == "__main__":
    run_split_audit()
