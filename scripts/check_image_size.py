from PIL import Image
import sys
import os

def check_image(path):
    if not os.path.exists(path):
        print(f"Error: {path} does not exist")
        return
    try:
        with Image.open(path) as img:
            w, h = img.size
            print(f"Dimensions: {w}x{h}")
            if w < 1600:
                print(f"WARNING: Width {w} is less than 1600px")
    except Exception as e:
        print(f"Error reading image: {e}")

if __name__ == "__main__":
    check_image(sys.argv[1])
