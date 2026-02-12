import re
import os

def get_style_colors(content_xml_path):
    if not os.path.exists(content_xml_path):
        return {}
    
    with open(content_xml_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml = f.read()
    
    # Extract automatic styles that have background colors
    # Example: <style:style style:name="ce1" style:family="table-cell" ...>
    #          <style:table-cell-properties fo:background-color="#00ff00"/>
    #          </style:style>
    
    style_map = {}
    # Use a simpler regex to find style blocks
    style_blocks = re.findall(r'<style:style style:name="([^"]+)" style:family="table-cell"[^>]*>(.*?)</style:style>', xml, re.DOTALL)
    
    for style_name, content in style_blocks:
        color_match = re.search(r'fo:background-color="([^"]+)"', content)
        if color_match:
            style_map[style_name] = color_match.group(1).lower()
            
    return style_map

if __name__ == "__main__":
    print("Daily.ods Styles:")
    daily_styles = get_style_colors('temp_daily/content.xml')
    for name, color in list(daily_styles.items())[:10]:
        print(f"  {name}: {color}")
        
    print("\nTotal2.ods Styles:")
    total_styles = get_style_colors('temp_total2/content.xml')
    for name, color in list(total_styles.items())[:10]:
        print(f"  {name}: {color}")
