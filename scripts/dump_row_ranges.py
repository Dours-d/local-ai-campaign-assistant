import re
import os

def get_row_range(table_xml, start_idx, end_idx):
    # indices are 0-based
    row_pattern = re.compile(r'<table:table-row.*?>(.*?)</table:table-row>', re.DOTALL)
    rows = row_pattern.finditer(table_xml)
    
    current_row = 0
    results = []
    for match in rows:
        row_content = match.group(1)
        row_tag = match.group(0)[:match.group(0).find('>')+1]
        
        repeat_match = re.search(r'table:number-rows-repeated="(\d+)"', row_tag)
        repeat_count = int(repeat_match.group(1)) if repeat_match else 1
        
        # Check if any row in this segment is within our range
        segment_start = current_row
        segment_end = current_row + repeat_count - 1
        
        if not (segment_end < start_idx or segment_start > end_idx):
            # There is overlap
            results.append({
                'range': (segment_start, segment_end),
                'content': row_content,
                'tag': row_tag
            })
            
        current_row += repeat_count
        if current_row > end_idx:
            break
    return results

content_path = 'temp_total2/content.xml'
with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = f.read()

def dump_sheet_range(sheet_name, start_row, end_row):
    print(f"\n--- DUMPING {sheet_name} ROWS {start_row}-{end_row} ---")
    match = re.search(f'table:name="{sheet_name}"', data, re.IGNORECASE)
    if not match:
        print(f"Sheet {sheet_name} not found")
        return
    
    s_start = match.start()
    s_end = data.find('</table:table>', s_start)
    table_xml = data[s_start:s_end]
    
    ranges = get_row_range(table_xml, start_row-1, end_row-1)
    for r in ranges:
        print(f"Rows {r['range'][0]+1}-{r['range'][1]+1}:")
        print(f"Tag: {r['tag']}")
        # Print a bit of content, or look for annotations
        if '<office:annotation' in r['content']:
            print("!!! FOUND ANNOTATION IN THIS ROW SEGMENT !!!")
            anns = re.findall(r'<office:annotation.*?</office:annotation>', r['content'], re.DOTALL)
            for i, ann in enumerate(anns):
                print(f"  Annotation {i+1}: {' '.join(re.findall(r'<text:p>(.*?)</text:p>', ann))}")
        print(f"XML: {r['content'][:1000]}...") # Print first 1000 chars of row content
        print("-" * 50)

dump_sheet_range('Rania', 160, 170)
dump_sheet_range('Ibtisam', 400, 420)
