# Failure Response Protocol: Onboarding Portal

This document formalizes the response steps for infrastructure outages affecting the Gaza Resilience Onboarding Portal and associated tunnels.

## 1. Automated Resilience (Self-Healing)
The `monitor_services.ps1` watchdog handles most common failures automatically.

| Scenario | Watchdog Action | User Impact |
| :--- | :--- | :--- |
| **Server Process Crash** | Automatic restart via `.venv/python.exe`. | < 30s downtime. |
| **Tunnel URL Timeout** | Retries 3 times, then fails over to next provider. | < 2m downtime; URL updates on GitHub. |
| **Git Sync Failure** | Retries on next loop; alerts sent to Discord/Slack. | Portal might show stale data. |

## 2. Operational Severity Levels

### [SEV 3] - Minor / Recovered
- **Indicator**: Automated failover triggered and succeeded.
- **Action**: Monitor logs in `data/monitoring.log` to ensure stability on the fallback provider.
- **Notification**: Alert sent to Discord/Slack.

### [SEV 2] - Targeted Failure
- **Indicator**: All automated tunnel providers (Cloudflare, LT, Ngrok) are failing or blocked.
- **Action**: 
    1. Check local internet connectivity.
    2. Verify `onboarding_server.py` is listening on port 5010.
    3. Manually restart the monitor: `Start_HeadQuarters.bat`.
- **Manual Failover**: Use a persistent VPN or Tailscale Funnel if public providers are throttled.

### [SEV 1] - Total Blackout
- **Indicator**: Local machine offline or hardware failure.
- **Emergency Steps**:
    1. Update the GitHub `index.html` redirector manually to point to a "Maintenance" or "Emergency Backup" page.
    2. Restore from the most recent backup in `/backups`.

## 3. Communication Protocol
In the event of a sustained SEV 2 or SEV 1:
1. **Internal Status**: Post a message in the private coordinator channel.
2. **Public Status**: Update the "Bridge UI" (`onboard.html`) with an emergency notice if possible.

## 4. Provider Failover Stack
The current automated sequence is:
1. **Cloudflare** (Primary - Highest stability)
2. **Localtunnel** (Secondary - Quick fallback)
3. **Ngrok** (Tertiary - Robust bypass)

---
*Last Updated: 2026-02-28*
