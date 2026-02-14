import json
import os
import sys
import io
from pathlib import Path

# Configure UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Get all submission files
submission_dir = Path('data/onboarding_submissions')
submission_files = list(submission_dir.glob('*_submission.json'))

print(f"Found {len(submission_files)} submission files")

# Filter out test/mock submissions
excluded_patterns = ['MOCK-USER-001', 'myself_submission', 'test_ping']
real_submissions = [f for f in submission_files if not any(x in f.name for x in excluded_patterns)]

print(f"Real targets identified: {len(real_submissions)}")

# Load and process submissions
campaigns_to_create = []

# Base directory for absolute paths
base_dir = Path(os.getcwd())

for file in real_submissions:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            sub = json.load(f)
        
        # 1. Determine Phone/ID
        phone = sub.get('whatsapp_number') or sub.get('beneficiary_id')
        if not phone:
            phone = file.stem.replace('_submission', '')
        if phone.startswith('viral_'):
            phone = phone.replace('viral_', '')
            
        # 2. Extract Title
        title = sub.get('title', 'Untitled Campaign')
        
        # 3. Extract Description
        description = sub.get('story') or sub.get('description')
        if not description and sub.get('media'):
            description = sub.get('media')[0].get('description')
        if not description:
            description = f"Help support this campaign for {phone}."

        # 4. Extract Image Path
        image_path = sub.get('image')
        if not image_path and sub.get('media'):
            image_path = sub.get('media')[0].get('path')
        
        # Fallback: check media subfolder if image_path is missing or doesn't exist
        if not image_path or not os.path.exists(os.path.join(base_dir, image_path)):
            id_media_dir = submission_dir / 'media' / phone
            if id_media_dir.exists():
                images = list(id_media_dir.glob('*.*'))
                if images:
                    image_path = str(images[0].relative_to(base_dir))

        # Check final image path
        abs_image_path = os.path.join(base_dir, image_path) if image_path else ""
        
        if image_path and os.path.exists(abs_image_path):
            campaign = {
                "bid": phone,
                "title": title,
                "description": description,
                "goal": sub.get('goal', 5000),
                "image": abs_image_path
            }
            campaigns_to_create.append(campaign)
            print(f"✓ {phone}: {title[:50]}")
        else:
            print(f"✗ {phone}: Missing image - looked in {image_path or 'nowhere'}")
            
    except Exception as e:
        print(f"Error processing {file.name}: {e}")

print(f"\n✅ {len(campaigns_to_create)} campaigns ready to create")

# Save to batch file
with open('data/new_trustees_batch.json', 'w', encoding='utf-8') as f:
    json.dump(campaigns_to_create, f, ensure_ascii=False, indent=2)

print(f"✅ Saved to data/new_trustees_batch.json")
