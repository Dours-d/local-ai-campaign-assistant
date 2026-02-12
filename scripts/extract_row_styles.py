import re
import html

def extract_row_styles(xml_path, sheet_name):
    with open(xml_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml = f.read()
    
    match = re.search(f'table:name="{sheet_name}"', xml)
    if not match:
        return []
    
    start = match.start()
    end = xml.find('</table:table>', start)
    sheet_xml = xml[start:end]
    
    row_pattern = re.compile(r'<table:table-row table:style-name="([^"]+)"[^>]*>(.*?)</table:table-row>', re.DOTALL)
    
    results = []
    for i, r_match in enumerate(row_pattern.finditer(sheet_xml)):
        style_name = r_match.group(1)
        row_content = r_match.group(2)
        
        # Extract donor/campaign info for context
        p_matches = re.findall(r'<text:p>(.*?)</text:p>', row_content)
        context = " ".join(p_matches[:3]) # First 3 fields
        
        results.append((i, style_name, context))
        if i > 100: break
    
    return results

if __name__ == "__main__":
    print("Daily.ods Payments Row Styles:")
    rows = extract_row_styles('temp_daily/content.xml', 'Payments')
    for i, style, ctx in rows[:30]:
        print(f"Row {i} (Style {style}): {ctx}")
