
# Infomaniak VPS Deployment Guide

This guide explains how to move your project from your local computer to an Infomaniak VPS Lite (€3/month) for 24/7 operation.

## 1. Get your VPS
1. Sign up at [Infomaniak](https://www.infomaniak.com/).
2. Select **Cloud Computing > VPS Lite**.
3. Choose **Ubuntu 22.04 LTS** as the Operating System.

## 2. Server Preparation
Connect to your VPS via SSH and run:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y
```

## 3. Clone and Setup
```bash
git clone <your-private-repo-url>
cd local_ai_campaign_assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Environment Variables
To keep your server secure, set your passwords as environment variables in your server's `.bashrc` or a `.env` file:
```bash
export ADMIN_PASSWORD="your_secure_password"
export ADMIN_SECRET_KEY="some_random_string"
```

## 5. Running the Services
Since you are on a VPS, you don't need a tunnel to `localhost`. You can run the server and access it via the VPS IP or a domain.

To keep it running after you close SSH, use `pm2` or `systemd`:
```bash
# Example with nohup for quick start
nohup python3 scripts/onboarding_server.py &
```

## 6. Cloudflare Tunnel (Optional but Recommended)
You can still run `scripts/start_tunnel.py` on the VPS to get a nice `.trycloudflare.com` URL, or better yet, link it to your own domain using the Cloudflare Dashboard.
