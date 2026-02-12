import requests

CDP_URL = "http://127.0.0.1:9222/json"

def main():
    try:
        r = requests.get(CDP_URL).json()
        print(f"Debugger active tabs: {len(r)}")
        for t in r:
            if 'whydonate.com' not in t.get('url', '') and t['type'] == 'page':
                print(f"Closing tab: {t['url']}")
                requests.get(f"http://127.0.0.1:9222/json/close/{t['id']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
