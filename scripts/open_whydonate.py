import requests, time
def open_url():
    try:
        # Use simple URL to avoid JSON parsing issues if it redirects
        url = "http://127.0.0.1:9222/json/new?https://whydonate.com/fundraising/start"
        r = requests.get(url)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    open_url()
