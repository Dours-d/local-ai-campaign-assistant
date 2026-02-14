import json
import os
from pathlib import Path

def extract_all_real_data():
    dir_path = Path('data/onboarding_submissions')
    real_files = [f for f in dir_path.glob('*_submission.json') if not any(x in f.name for x in ['MOCK-USER-001', 'myself_submission', 'test_ping'])]
    
    data_list = []
    media_dir = dir_path / 'media'
    
    for f in real_files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Identify core ID
            bid = data.get('beneficiary_id')
            if not bid:
                bid = f.stem.replace('_submission', '')
            
            clean_bid = bid.replace('viral_', '')
            
            # Extract basic info
            title = data.get('title') or ""
            story = data.get('story') or data.get('description') or ""
            
            # If still empty, check media array
            media_list = data.get('media', [])
            if not title and media_list:
                for m in media_list:
                    if m.get('title'):
                        title = m['title']
                        break
            
            if not story and media_list:
                for m in media_list:
                    if m.get('description'):
                        story = m['description']
                        break
            
            # Image mapping
            image_path = None
            # Check JSON field
            if data.get('image') and os.path.exists(data['image']):
                image_path = data['image']
            
            # Check media array
            if not image_path and media_list:
                for m in media_list:
                    if m.get('path') and os.path.exists(m['path']):
                        image_path = m['path']
                        break
            
            # Search media folder
            if not image_path:
                # Look for folder with clean_bid
                bid_folder = media_dir / clean_bid
                if bid_folder.exists():
                    images = list(bid_folder.glob('*.*'))
                    if images:
                        image_path = str(images[0].absolute())
                else:
                    # Generic search if folder not found
                    for root, dirs, files in os.walk(media_dir):
                        if clean_bid in root:
                            for img_f in files:
                                if any(img_f.lower().endswith(ext) for ext in ['.jpg', '.png', '.jpeg']):
                                    image_path = str(Path(root) / img_f)
                                    break
                        if image_path: break

            data_list.append({
                "bid": bid,
                "clean_id": clean_bid,
                "whatsapp": data.get('whatsapp_number') or clean_bid,
                "title": title,
                "story": story,
                "image": image_path,
                "source_file": f.name
            })
        except Exception as e:
            print(f"Error reading {f.name}: {e}")
            
    with open('data/extracted_real_submissions.json', 'w', encoding='utf-8') as out:
        json.dump(data_list, out, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(data_list)} real submissions to data/extracted_real_submissions.json")

if __name__ == "__main__":
    extract_all_real_data()
