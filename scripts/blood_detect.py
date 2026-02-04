
from PIL import Image
import numpy as np

def check_for_blood(image_path, threshold=0.05):
    """
    Scans an image for 'blood-red' pixel density.
    Returns (is_flagged, percentage_detected)
    """
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((200, 200)) # Downsample for speed
        data = np.array(img)
        
        reds = data[:, :, 0]
        greens = data[:, :, 1]
        blues = data[:, :, 2]
        
        # Heuristic: High Red (>100), Low Green/Blue (<60), and Red significantly dominant
        # This covers wet blood (bright red) and dried blood (dark red)
        blood_mask = (reds > 80) & (greens < 60) & (blues < 60) & (reds > (greens.astype(np.int16) + blues.astype(np.int16)))
        
        blood_pixel_count = np.sum(blood_mask)
        total_pixels = data.shape[0] * data.shape[1]
        ratio = blood_pixel_count / total_pixels
        
        return ratio > threshold, ratio
        
    except Exception as e:
        print(f"Error scanning {image_path}: {e}")
        return False, 0.0

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        flagged, pct = check_for_blood(sys.argv[1])
        print(f"Flagged: {flagged} ({pct:.2%})")
