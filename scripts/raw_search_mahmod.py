import re
import os

def raw_search_mahmod(xml_path):
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
    print(f"Main table XML length: {len(main_xml)}")

    # Search for Mahmod with context
    matches = list(re.finditer(r'Mahmod', main_xml))
    print(f"Found {len(matches)} occurrences of 'Mahmod' in Main")
    
    for m in matches[:10]:
        # Find the row containing this match
        row_start = main_xml.rfind('<table:table-row', 0, m.start())
        row_end = main_xml.find('</table:table-row>', m.end())
        row_content = main_xml[row_start:row_end+18]
        print(f"\n--- ROW MATCH ---")
        # Strip internal tags for readability
        clean_row = re.sub(r'<[^>]+>', ' ', row_content)
        print(f"Clean content: {clean_row.strip()}")
        print(f"Raw row: {row_content}")

if __name__ == "__main__":
    raw_search_mahmod('temp_total2/content.xml')
