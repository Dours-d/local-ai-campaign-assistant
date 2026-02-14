import os
import re
from pathlib import Path

def update_messages():
    links_file = Path('data/created_campaigns.txt')
    if not links_file.exists():
        print("No created_campaigns.txt found yet.")
        return

    msg_dir = Path('data/trustee_messages')
    if not msg_dir.exists():
        print("Trustee messages directory not found.")
        return

    # Parse created campaigns
    # Format: bid: url
    links = {}
    with open(links_file, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                bid, url = line.split(':', 1)
                links[bid.strip()] = url.strip()

    print(f"Found {len(links)} links to process.")

    # Update messages
    updated_count = 0
    for bid, url in links.items():
        # Match by bid in filename (whatsapp number is used in filename)
        # We need to find the file that contains this bid in its name
        found_files = list(msg_dir.glob(f"*{bid}*_status_update.txt"))
        
        for msg_file in found_files:
            with open(msg_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace placeholder or append
            if "We will send you the link as soon as it is live" in content:
                ar_link_text = f"رابط حملتك هو: {url}"
                en_link_text = f"Your campaign link is: {url}"
                
                content = content.replace(
                    "نحن نقوم بإعداد حملتك على WhyDonate. سنرسل لك الرابط بمجرد نشره.",
                    f"لقد تم نشر حملتك بنجاح على WhyDonate!\n{ar_link_text}"
                )
                content = content.replace(
                    "We are preparing your campaign on WhyDonate. We will send you the link as soon as it is live.",
                    f"Your campaign is now live on WhyDonate!\n{en_link_text}"
                )
                
                with open(msg_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {msg_file.name} with link.")
                updated_count += 1

    print(f"Successfully updated {updated_count} messages.")

if __name__ == "__main__":
    update_messages()
