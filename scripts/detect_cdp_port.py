
import requests
import socket

IPS = ['127.0.0.1', '100.118.2.43', '192.168.1.110']
PORTS = [92, 9222, 9223, 9224, 9333]

def check_cdp():
    for ip in IPS:
        for port in PORTS:
            url = f"http://{ip}:{port}/json"
            print(f"Checking {url}...", end=" ")
            try:
                resp = requests.get(url, timeout=1)
                if resp.status_code == 200:
                    print("SUCCESS!")
                    print(resp.text)
                    return
                else:
                    print(f"Status: {resp.status_code}")
            except Exception as e:
                print("Failed")

if __name__ == "__main__":
    check_cdp()
