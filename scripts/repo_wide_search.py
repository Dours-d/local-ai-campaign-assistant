import os

def main():
    targets = ["130620", "126397", "chuffed.org"]
    print(f"Searching repository for: {targets}...")
    
    count = 0
    for root, dirs, files in os.walk("."):
        # Skip .git and common large non-data folders
        if ".git" in dirs: dirs.remove(".git")
        if "node_modules" in dirs: dirs.remove("node_modules")
        
        for file in files:
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = [t for t in targets if t in content]
                    if matches:
                        print(f"MATCH in {path}: {matches}")
                        # Print context for first match
                        idx = content.find(matches[0])
                        start = max(0, idx - 100)
                        end = min(len(content), idx + 200)
                        print(f"CONTEXT: ...{content[start:end]}...")
                        print("-" * 20)
                        count += 1
            except Exception:
                pass

    print(f"Search complete. Found matches in {count} files.")

if __name__ == "__main__":
    main()
