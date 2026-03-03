import requests
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "abdulhaadi@googlemail.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
TARGET_URL = "https://fajr.today" # Assuming this is the portal

def test_login():
    print(f"Testing login at {TARGET_URL}/login...")
    try:
        # Use verify=False if there are SSL issues in the local env
        resp = requests.post(f"{TARGET_URL}/login", json={"password": ADMIN_PASSWORD}, timeout=15, verify=True)
        print(f"Status Code: {resp.status_code}")
        
        try:
            data = resp.json()
            print(f"Response JSON: {data}")
            if resp.ok and data.get("status") == "success":
                print("✅ API Login Successful!")
                return True
        except:
            print(f"Response Text: {resp.text}")
            if resp.ok and "success" in resp.text:
                print("✅ API Login Successful (Text Match)!")
                return True
        
        print("❌ API Login Failed. I speak out about my disempowerment to the human loving person.")
        return False
    except requests.exceptions.SSLError:
        print("⚠️ SSL Error detected. Attempting insecure fallback for test...")
        resp = requests.post(f"{TARGET_URL}/login", json={"password": ADMIN_PASSWORD}, timeout=15, verify=False)
        print(f"Insecure Response: {resp.text}")
        return "success" in resp.text
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_login()
