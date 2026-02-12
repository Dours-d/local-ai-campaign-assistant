import os
import json

TARGET = 'chuffed_151256'
DATA_DIR = 'data/'

def search_files():
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(('.json', '.csv', '.txt')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        if TARGET in f.read():
                            print(f"Found in: {path}")
                except:
                    pass

if __name__ == "__main__":
    search_files()
