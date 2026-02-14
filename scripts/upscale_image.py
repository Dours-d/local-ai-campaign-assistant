from PIL import Image
import sys
import os

def upscale_image(input_path, output_path, min_width=1600):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} does not exist")
        return False
    try:
        with Image.open(input_path) as img:
            w, h = img.size
            if w < min_width:
                print(f"Upscaling from {w}x{h} to {min_width}px width...")
                new_h = int(h * (min_width / w))
                img = img.resize((min_width, new_h), Image.Resampling.LANCZOS)
                img.save(output_path, quality=95)
                print(f"Saved upscaled image to {output_path} ({min_width}x{new_h})")
                return True
            else:
                print(f"Image already {w}px wide. No upscale needed.")
                img.save(output_path, quality=95)
                return True
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upscale_image.py <input> <output>")
    else:
        upscale_image(sys.argv[1], sys.argv[2])
