import os
import re

def clean_relay_calls(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find initiateRelayGift calls and clean up multi-space names
    def clean_spaces(match):
        func_call = match.group(0)
        # Replace multiple spaces/newlines with a single space inside the string literals
        clean_call = re.sub(r'\s{2,}', ' ', func_call)
        return clean_call

    new_content = re.sub(r"initiateRelayGift\([^)]+\)", clean_spaces, content)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Cleaned up relay calls in {html_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_file = os.path.join(base_dir, 'frontend', 'campaigns.html')
    clean_relay_calls(html_file)
