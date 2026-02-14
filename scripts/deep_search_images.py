import os
from pathlib import Path

missing = [
    '972567243079', '+0797172654', '+970567419045', 
    '+972599197456', '0592115058', '0595843932', 
    '0597172654', '0599560696', 'anon_c3a16664'
]

media_dir = Path('data/onboarding_submissions/media')

print(f"Searching for images in {media_dir}...")

found_map = {}

for m in missing:
    clean = m.replace('+', '').replace('viral_', '')
    print(f"Target: {m} (Clean: {clean})")
    
    found = False
    for root, dirs, files in os.walk(media_dir):
        # Check folder name
        if clean in Path(root).name:
            for f in files:
                if any(f.lower().endswith(ext) for ext in ['.jpg', '.png', '.jpeg']):
                    path = os.path.join(root, f)
                    print(f"  ✓ Found in folder: {path}")
                    found_map[m] = str(Path(path).absolute())
                    found = True
                    break
        if found: break
        
        # Check filename
        for f in files:
            if clean in f:
                if any(f.lower().endswith(ext) for ext in ['.jpg', '.png', '.jpeg']):
                    path = os.path.join(root, f)
                    print(f"  ✓ Found in filename: {path}")
                    found_map[m] = str(Path(path).absolute())
                    found = True
                    break
        if found: break

    if not found:
        print("  ✗ No match found")

print("\nFinal Discovery Map:")
for k, v in found_map.items():
    print(f"{k}: {v}")

# Output for next script to use
import json
with open('data/discovered_missing_images.json', 'w', encoding='utf-8') as f:
    json.dump(found_map, f, indent=2)
