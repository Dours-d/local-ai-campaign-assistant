import json
import os
import re
from pathlib import Path

def find_content_and_images():
    dir_path = Path('data/onboarding_submissions')
    media_dir = dir_path / 'media'
    base_dir = Path(os.getcwd())
    
    results = []
    
    # 1. Map all potential images in media dir
    image_map = {}
    for root, dirs, files in os.walk(media_dir):
        for f in files:
            if any(f.lower().endswith(ext) for ext in ['.jpg', '.png', '.jpeg']):
                full_path = os.path.join(root, f)
                parent = Path(root).name
                if parent not in image_map:
                    image_map[parent] = []
                image_map[parent].append(full_path)

    all_json = list(dir_path.glob('*.json'))
    for f in all_json:
        if any(x in f.name for x in ['MOCK-USER-001', 'myself_submission', 'test_ping']):
            continue
            
        try:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
                data = json.loads(content)
            
            bid = data.get('beneficiary_id') or f.stem.replace('_submission', '')
            clean_id = bid.replace('viral_', '')
            
            has_arabic = bool(re.search(r'[\u0600-\u06FF]', content))
            
            title = data.get('title') or ""
            story = data.get('story') or data.get('description') or ""
            
            media_list = data.get('media', [])
            if not title and media_list:
                for m in media_list:
                    if m.get('title'): title = m['title']; break
            if not story and media_list:
                for m in media_list:
                    if m.get('description'): story = m['description']; break
            
            image = None
            json_img = data.get('image') or (media_list[0].get('path') if media_list else None)
            if json_img and os.path.exists(json_img):
                image = json_img
            
            if not image:
                if clean_id in image_map:
                    image = image_map[clean_id][0]
                elif bid in image_map:
                    image = image_map[bid][0]
            
            results.append({
                "file": f.name,
                "id": clean_id,
                "has_arabic": has_arabic,
                "title": title,
                "story": story,
                "image": image if not image else str(Path(image).absolute())
            })
            
        except Exception as e:
            print(f"Error processing {f.name}: {e}")
            
    with open('data/detailed_submission_map.json', 'w', encoding='utf-8') as out:
        json.dump(results, out, indent=2, ensure_ascii=False)
    
    print(f"Mapped {len(results)} files to data/detailed_submission_map.json")

if __name__ == "__main__":
    find_content_and_images()
