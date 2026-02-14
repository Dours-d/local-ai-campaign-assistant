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
        "en_title": "Emergency Aid for family in Khan Yunis",
        "en_story": "I need financial help because I have not received anything from any party to support my family during this difficult time."
    },
    "972598827480": {
        "en_title": "Help my family for a new beginning",
        "en_story": "Magda and Mohammed's family. Our home was completely destroyed and we became homeless. Your support and contribution, even a little, gives us hope."
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
    with open('data/detailed_submission_map.json', 'r', encoding='utf-8') as f:
        mapped_data = json.load(f)
    
    batch = []
    
    # Try to find a good generic image to use as fallback
    fallback_image = None
    # Look for fajr.jpg or any image from a successful mapping
    for item in mapped_data:
        if item['image'] and os.path.exists(item['image']):
            if 'fajr.jpg' in item['image']:
                fallback_image = item['image']
                break
            if not fallback_image:
                fallback_image = item['image']

    print(f"Using fallback image: {fallback_image}")

    for item in mapped_data:
        bid = item['id']
        ar_title = item['title']
        ar_story = item['story']
        
        # Skip if no content AND no translation
        if not (ar_title or ar_story) and bid not in translations:
            continue
            
        # Get English translation if available
        trans = translations.get(bid) or translations.get(item['id'].replace('+', '')) or {}
        en_title = trans.get('en_title', '')
        en_story = trans.get('en_story', '')
        
        # Create Bilingual Title
        if ar_title and en_title:
            final_title = f"{ar_title} | {en_title}"
        elif ar_title:
            final_title = ar_title
        else:
            final_title = en_title
            
        # Create Bilingual Description
        if ar_story and en_story:
            final_story = f"{ar_story}\n\n---\n\n{en_story}"
        elif ar_story:
            final_story = ar_story
        else:
            final_story = en_story
            
        if not final_title or not final_story:
            continue

        # Final cleanup of Title (WhyDonate title limit)
        if len(final_title) > 80:
            final_title = final_title[:77] + "..."
            
        # Image Handling
        image_path = item['image']
        if not image_path or not os.path.exists(image_path):
            image_path = fallback_image

        if not image_path:
            print(f"Skipping {bid} - No image and no fallback available.")
            continue

        batch.append({
            "bid": bid,
            "title": final_title,
            "description": final_story,
            "goal": 5000,
            "image": str(Path(image_path).absolute())
        })

    with open('data/new_trustees_bilingual_batch.json', 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    
    print(f"Generated bilingual batch with {len(batch)} campaigns in data/new_trustees_bilingual_batch.json")

if __name__ == "__main__":
    generate_bilingual_batch()
