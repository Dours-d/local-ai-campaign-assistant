# Tailscale Funnel Setup Guide

Since Tailscale processes require system-level installation and browser-based login, I cannot automate the installation entirely. Follow these 3 steps to get your Permanent Link.

## Step 1: Install Tailscale
1.  **Download**: [Download Tailscale for Windows](https://tailscale.com/download/windows)
2.  **Install**: Run the installer. It takes about 1 minute.
3.  **Login**:
    *   Click the Tailscale icon in your system tray (near the clock).
    *   Log in with any Google/Microsoft account.

## Step 2: Enable "Funnel" (The Public Proxy)
Tailscale Funnel is an "opt-in" feature.
1.  Go to the [Tailscale Admin Console](https://login.tailscale.com/admin/acls).
2.  In **Access Controls**, add this to the config file (or just click "Enable Funnel" if you see a button):
    *   *Note: Usually, just running the command below triggers the setup wizard.* [Read Guide if needed](https://tailscale.com/kb/1223/funnel)

## Step 3: Run the Funnel
Once installed, open a **new** PowerShell terminal (Run as Administrator) and type:

```powershell
tailscale funnel 5000
```

## What happens then?
1.  Tailscale will give you a **Permanent URL** like `https://gael-pc.tailnet-name.ts.net`.
2.  **This URL never changes.**
3.  It handles HTTPS (SSL) automatically.
4.  It bypasses your router safely.

---

### Once you have the URL:
1.  Paste it here so I can update your `monitor_services.ps1` script to use *that* URL instead of trying to find random Cloudflare ones.
