import re
import os

def sum_mahmod_raised(xml_path):
    if not os.path.exists(xml_path):
        print(f"File not found: {xml_path}")
        return

    with open(xml_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()

    main_match = re.search(r'table:name="Main"', data)
    if not main_match:
        print("Main table not found")
        return

    start = main_match.start()
    end = data.find('</table:table>', start)
    main_xml = data[start:end]

    # Patterns for the campaign title variations
    pattern_mahmod = re.compile(r'Help Mahmod\s+rebuild his life', re.IGNORECASE)
    pattern_mahmoud = re.compile(r'Help Mahmoud\s+rebuild his life', re.IGNORECASE)
    
    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', main_xml, re.DOTALL))
    
    mahmod_stats = {'count': 0, 'eur': 0.0, 'aud': 0.0, 'usd': 0.0, 'gbp': 0.0}
    mahmoud_stats = {'count': 0, 'eur': 0.0, 'aud': 0.0, 'usd': 0.0, 'gbp': 0.0}
    
    for row_match in rows:
        row_content = row_match.group(1)
        clean_row_text = re.sub(r'<[^>]+>', ' ', row_content)
        clean_row_text = re.sub(r'\s+', ' ', clean_row_text).strip()

        target = None
        if pattern_mahmod.search(clean_row_text): target = mahmod_stats
        elif pattern_mahmoud.search(clean_row_text): target = mahmoud_stats
        
        if target:
            # Check payment in AB (index 27)
            cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell).*?(/|>(.*?)</\1)>', re.DOTALL)
            cell_matches = cell_pattern.finditer(row_content)
            row_cells = []
            for cm in cell_matches:
                cell_xml = cm.group(0)
                rep_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
                rep_count = int(rep_match.group(1)) if rep_match else 1
                val = 0.0
                v_match = re.search(r'office:value="([\d.]+)"', cell_xml)
                if v_match: val = float(v_match.group(1))
                else:
                    p_match = re.search(r'<text:p>(.*?)</text:p>', cell_xml)
                    if p_match:
                        try: val = float(p_match.group(1).replace(',', ''))
                        except: val = 0.0
                text_p = ""
                p_match = re.search(r'<text:p>(.*?)</text:p>', cell_xml)
                if p_match: text_p = p_match.group(1)
                for _ in range(rep_count):
                    row_cells.append({'val': val, 'text': text_p})
            
            payment = row_cells[27]['val'] if len(row_cells) > 27 else 0.0
            
            if payment == 0:
                target['count'] += 1
                if len(row_cells) > 5:
                    amount = row_cells[4]['val']
                    currency = row_cells[5]['text'].lower()
                    if currency == 'eur': target['eur'] += amount
                    elif currency == 'aud': target['aud'] += amount
                    elif currency == 'usd': target['usd'] += amount
                    elif currency == 'gbp': target['gbp'] += amount
                    else: target['eur'] += amount

    def print_stats(name, stats):
        print(f"Stats for '{name}':")
        print(f"  Count: {stats['count']}")
        print(f"  EUR: {stats['eur']:.2f} | AUD: {stats['aud']:.2f} | USD: {stats['usd']:.2f} | GBP: {stats['gbp']:.2f}")
        total_eur = stats['eur'] + (stats['aud'] * 0.61) + (stats['usd'] * 0.93) + (stats['gbp'] * 1.17)
        print(f"  Total EUR Equiv: {total_eur:.2f}")
        return total_eur

    e1 = print_stats("Mahmod", mahmod_stats)
    e2 = print_stats("Mahmoud", mahmoud_stats)
    print(f"\nGRAND TOTAL UNPAID IN MAIN: {e1 + e2:.2f} EUR")
    
if __name__ == "__main__":
    sum_mahmod_raised('temp_total2/content.xml')
