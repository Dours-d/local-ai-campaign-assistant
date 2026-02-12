import zipfile
import re

ODS_FILE = "total2_copy.ods"

def find_annotation_tags():
    try:
        with zipfile.ZipFile(ODS_FILE, 'r') as z:
            with z.open('content.xml') as f:
                content = f.read().decode('utf-8')
                
                # Find annotations
                annotations = re.findall(r'<office:annotation.*?</office:annotation>', content, re.DOTALL)
                print(f"Found {len(annotations)} annotations.")
                
                for i, ann in enumerate(annotations[:20]):
                    # Extract text content (inside <text:p>)
                    texts = re.findall(r'<text:p[^>]*>(.*?)</text:p>', ann, re.DOTALL)
                    clean_text = " ".join(texts)
                    # Remove other tags
                    clean_text = re.sub(r'<[^>]+>', '', clean_text)
                    print(f"\nAnnotation {i+1}:")
                    print(clean_text.strip())
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_annotation_tags()
