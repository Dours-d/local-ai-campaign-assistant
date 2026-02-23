import json
import os
from pathlib import Path

# Manual translations for the Arabic content found in submissions
translations = {
    "972567243079": {
        "en_title": "Help my family rebuild their home",
        "en_story": "I hope you can stand with me in building a new home and extend a helping hand to me instead of the home that was bombed and destroyed because of the war. May God reward you with all goodness."
    },
    "972597341113": {
        "en_title": "Emergency Aid: Near MSF Khan Yunis",
        "en_story": "Akram and his family are currently navigating the extreme hardships of displacement in Khan Yunis. They are located in the As-Sadaa area, in close proximity to the MSF (Doctors Without Borders) facility and Al-Qudra Supermarket. Despite being near these known landmarks, they have yet to receive any direct assistance from any organization. Akram is reaching out for urgent financial support to provide basic necessities for his family during this critical time."
    },
    "972598827480": {
        "en_title": "A New Beginning for Magda & Mohammed",
        "en_story": "Magda and Mohammed's family have faced the ultimate hardship of war: the complete and total destruction of their family home. Now homeless, they are seeking to rebuild their lives from the ground up. This campaign is a call for a 'New Beginning'—to provide this family with the stability and security they lost. Your contribution, no matter how small, offers a path toward dignity and a safe place to call home again."
    },
    "972599904464": {
        "en_title": "Help me rebuild my home",
        "en_story": "I support my family while suffering from heart disease. All my children are in school. We lost our clothes, our safety, and our home. We have no one else to turn to. Any support is deeply appreciated."
    },
    "+0797172654": {
        "en_title": "War-injured father of 14 needs your help",
        "en_story": "I am from Gaza, and my situation is dire. I am war-injured, living in a tent with my wife and 14 children. Our house is destroyed, and we lack food, water, and clothing. Please help us survive."
    },
    "+970567419045": {
        "en_title": "Emergency Shelter: Help us buy a tent",
        "en_story": "My family and I are displaced in Deir el-Balah, living in a torn tent with no source of income or food. We desperately need help to buy a proper tent to protect us."
    },
    "+9720595562213": {
        "en_title": "Urgent Medical and Food Aid for Displaced Family",
        "en_story": "I am living in an open, unprotected tent with my children and injured husband. My daughter needs medical treatment for her head, and we lack basic essentials like milk and diapers."
    },
    "+972592645759": {
        "en_title": "Support Raneen and her elderly mother in Gaza",
        "en_story": "I am Raneen, four months pregnant and a mother of two. My home was destroyed, and I am now living in a car garage without any shelter. I had a tent on the edge of the sea and my tent flew away. I support my widowed mother. My father was martyred and I have no sisters. My mother is an asthma patient and needs weekly treatment."
    },
    "+972595038299": {
        "en_title": "Support for family of 6 with heart patient father",
        "en_story": "We are a family of 6. My father is a heart patient and my mother is elderly. We lost our home and have no income. We are living in a camp with no means of assistance as we cannot return to our destroyed home."
    },
    "0567243079": {
        "en_title": "A Tent of Hope: Rebuilding our Lives",
        "en_story": "I am seeking help to rebuild our home which was destroyed in the war. I hope you can lend a helping hand to help us start again."
    },
    "0592115058": {
        "en_title": "Urgent Winter Aid for Mother of 10",
        "en_story": "I have 10 children and we are living in tragic conditions. We lack food, water, and winter clothes. I beg for your help to support my family in this desperate time."
    },
    "0597172654": {
        "en_title": "Emergency Relief for family in Gaza",
        "en_story": "I need financial assistance to feed my children. We have no source of income and are struggling to survive."
    },
    "0598289338": {
        "en_title": "Urgent Support for pregnant mother and family",
        "en_story": "My situation is critical. My wife is pregnant and in danger, and we are in desperate need of food, clothing, shelter, and baby supplies. Any help will make a difference for us."
    },
    "0599560696": {
        "en_title": "Help Mohammed pursue his dream of Dentistry",
        "en_story": "I am 20 years old and determined to study dentistry despite the war destryoing our lives. My father was recently released after being detained, and I managed to pass my exams with high marks. I need support to register for university and continue my education."
    }
}

def generate_bilingual_batch():
    # Detect Vault vs Public Data
    base_dir = Path(__file__).parent.parent
    vault_dir = base_dir / 'vault'
    data_dir = base_dir / 'data'
    is_private = vault_dir.exists()
    root_src = vault_dir if is_private else data_dir
    
    submissions_map_path = root_src / 'detailed_submission_map.json'
    if not submissions_map_path.exists():
        submissions_map_path = data_dir / 'detailed_submission_map.json'

    with open(submissions_map_path, 'r', encoding='utf-8') as f:
        mapped_data = json.load(f)
    
    batch = []
    
    # Try to find a good generic image to use as fallback
    fallback_image = None
    media_dir = root_src / 'onboarding_submissions' / 'media'
    if media_dir.exists():
        images = list(media_dir.glob('**/*.jpg')) + list(media_dir.glob('**/*.jpeg')) + list(media_dir.glob('**/*.png'))
        if images:
            fallback_image = str(images[0])
            print(f"Using discovered fallback image: {fallback_image}")

    for item in mapped_data:
        bid = item['id']
        ar_title = item['title']
        ar_story = item['story']
        
        # Skip if no content AND no translation
        if not (ar_title or ar_story) and bid not in translations:
            continue
            
        trans = translations.get(bid) or translations.get(item['id'].replace('+', '')) or {}
        en_title = trans.get('en_title', '')
        en_story = trans.get('en_story', '')
        
        # Consistent Ordering: English | Arabic
        if ar_title and en_title:
            final_title = f"{en_title} | {ar_title}"
        elif ar_title:
            final_title = ar_title
        else:
            final_title = en_title
            
        if ar_story and en_story:
            final_story = f"{ar_story}\n\n---\n\n{en_story}"
        elif ar_story:
            final_story = ar_story
        else:
            final_story = en_story
            
        if not final_title or not final_story:
            continue

        # Enforce 75 character limit
        if len(final_title) > 75:
            final_title = final_title[:72] + "..."
            
        # Image Handling with Vault-First redirection
        image_path = item.get('image')
        if image_path:
            # If path in JSON contains 'data' but 'vault' exists, pivot to vault
            if is_private and '\\data\\' in image_path:
                image_path = image_path.replace('\\data\\', '\\vault\\')
            
            if not os.path.exists(image_path):
                image_path = fallback_image
        else:
            image_path = fallback_image

        if not image_path or not os.path.exists(image_path):
            print(f"Skipping {bid} - No valid image found.")
            continue

        batch.append({
            "bid": bid,
            "title": final_title,
            "description": final_story,
            "goal": 5000,
            "image": str(Path(image_path).absolute())
        })

    output_path = root_src / 'new_trustees_bilingual_batch.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    
    print(f"Generated bilingual batch with {len(batch)} campaigns in {output_path}")

if __name__ == "__main__":
    generate_bilingual_batch()
