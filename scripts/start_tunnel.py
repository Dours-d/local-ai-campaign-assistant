
import os
import sys
import subprocess
import urllib.request

def start_tunnel():
    work_dir = os.getcwd()
    exe_path = os.path.join(work_dir, "cloudflared.exe")

    if not os.path.exists(exe_path):
        print("Cloudflared not found. Downloading portable version...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        try:
            urllib.request.urlretrieve(url, exe_path)
            print("Download complete.")
        except Exception as e:
            print(f"Failed to download cloudflared: {e}")
            return

    print("\nStarting Seamless Tunnel for Onboarding Portal...")
    print("The link below starting with https://... will be PASSWORD-FREE for users.\n")

    try:
        # Run cloudflared tunnel
        # We use shell=False to avoid needing a shell environment
        subprocess.run([exe_path, "tunnel", "--url", "http://localhost:5000"])
    except KeyboardInterrupt:
        print("\nTunnel stopped by user.")
    except Exception as e:
        print(f"Error running tunnel: {e}")

if __name__ == "__main__":
    start_tunnel()
