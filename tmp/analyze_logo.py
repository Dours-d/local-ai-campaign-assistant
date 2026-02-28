from PIL import Image
import sys

def find_horizon(image_path):
    img = Image.open(image_path).convert('RGBA')
    width, height = img.size
    data = img.getdata()
    
    first_visible = -1
    last_visible = -1
    
    for y in range(height):
        # Extract row alpha channel
        row_alpha = [img.getpixel((x, y))[3] for x in range(width)]
        visible = any(a > 0 for a in row_alpha)
        if visible:
            if first_visible == -1:
                first_visible = y
            last_visible = y
            
    visible_height = last_visible - first_visible + 1
    print(f"Dimensions: {width}x{height}")
    print(f"Visible Row Range: {first_visible} to {last_visible} ({visible_height}px)")
    
    # Analyze density to find the "horizon"
    # Often the horizon is at the bottom of the main mark.
    # We can also look for a horizontal line with many opaque pixels.
    max_opaque = 0
    horizon_row = -1
    for y in range(first_visible, last_visible + 1):
        opaque_count = sum(1 for x in range(width) if img.getpixel((x,y))[3] > 200)
        if opaque_count > max_opaque:
            max_opaque = opaque_count
            horizon_row = y
            
    print(f"Likely Horizon Row (most opaque): {horizon_row}")
    if height > 0:
        print(f"Ratio from top: {horizon_row / height:.4f}")
        print(f"Ratio from visible top: {(horizon_row - first_visible) / visible_height:.4f}")


if __name__ == "__main__":
    find_horizon(sys.argv[1])
