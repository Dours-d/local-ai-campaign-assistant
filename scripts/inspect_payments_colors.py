import re
import html
import os

def get_style_colors(content_xml_path):
    if not os.path.exists(content_xml_path):
        return {}
    with open(content_xml_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml = f.read()
    style_map = {}
    style_blocks = re.findall(r'<style:style style:name="([^"]+)" style:family="table-cell"[^>]*>(.*?)</style:style>', xml, re.DOTALL)
    for style_name, content in style_blocks:
        color_match = re.search(r'fo:background-color="([^"]+)"', content)
        if color_match:
            style_map[style_name] = color_match.group(1).lower()
    return style_map

def is_green(hex_color):
    if not hex_color or not hex_color.startswith('#'): return False
    # Simple check for green dominance
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        return g > r and g > b and g > 150 # Bright/light green
    except:
        return False

def search_green_rows(xml_path, sheet_name, color_map):
    with open(xml_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml = f.read()
    
    match = re.search(f'table:name="{sheet_name}"', xml)
    if not match: return
    
    start = match.start()
    end = xml.find('</table:table>', start)
    sheet_xml = xml[start:end]
    
    row_pattern = re.compile(r'<table:table-row.*?>(.*?)</table:table-row>', re.DOTALL)
    cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell) table:style-name="([^"]+)"[^>]*>(.*?)</\1>', re.DOTALL)
    
    found = 0
    for i, r_match in enumerate(row_pattern.finditer(sheet_xml)):
        if i == 0: continue
        row_content = r_match.group(1)
        
        # Check all cells in row for a green background
        cells = cell_pattern.findall(row_content)
        row_colors = [color_map.get(c[1], "#ffffff") for c in cells]
        
        if any(is_green(c) for c in row_colors):
            text = " ".join(re.findall(r'<text:p>(.*?)</text:p>', row_content)[:3])
            print(f"Row {i}: GREEN FOUND. content={text}")
            found += 1
            if found > 10: break

if __name__ == "__main__":
    color_map = get_style_colors('temp_daily/content.xml')
    print("Searching for GREEN (Paid) rows in Payments Sheet:")
    search_green_rows('temp_daily/content.xml', 'Payments', color_map)
    
    # Also list ALL identified colors to double check
    all_colors = set(color_map.values())
    print(f"\nAll background colors in Daily.ods: {all_colors}")
