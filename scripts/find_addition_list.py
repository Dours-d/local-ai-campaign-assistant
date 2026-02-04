
import os
import re

FILE1 = "data/whatsapp_no_campaign.txt"
FILE2 = "data/campaignless_whatsapp.txt"

def normalize(number):
    # Keep digits, but handle the 972/970 prefix consistently
    digits = "".join(re.findall(r'\d+', str(number)))
    return digits

def find_delta():
    if not os.path.exists(FILE1) or not os.path.exists(FILE2):
        print("Required files not found.")
        return

    # Extract info from whatsapp_no_campaign.txt
    existing_normalized = set()
    with open(FILE1, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                normalized = normalize(line)
                if normalized:
                    existing_normalized.add(normalized)

    # Extract and normalize numbers from campaignless_whatsapp.txt
    new_numbers = []
    with open(FILE2, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('+'):
                normalized = normalize(line)
                if normalized and normalized not in existing_normalized:
                    new_numbers.append(line)
                    existing_normalized.add(normalized) # Avoid duplicates in the new list too

    print(f"\nFound {len(new_numbers)} numbers in campaignless_whatsapp.txt that are NOT in whatsapp_no_campaign.txt:")
    print("-" * 30)
    for num in new_numbers:
        print(num)
    print("-" * 30)

if __name__ == "__main__":
    find_delta()
