/**
 * SOVEREIGN AUDITOR: Google Apps Script Watchdog
 *
 * PURPOSE: Independently verify if the GitHub Pages redirect matches the actual tunnel.
 * HOW TO USE:
 * 1. Go to script.google.com
 * 2. Paste this code.
 * 3. Set a Time-based trigger (every 30 mins).
 */

const GITHUB_PAGES_URL = "https://dours-d.github.io/local-ai-campaign-assistant/index.html";

function auditPortal() {
    try {
        // 1. Fetch the GitHub redirector
        const response = UrlFetchApp.fetch(GITHUB_PAGES_URL);
        const html = response.getContentText();

        // 2. Extract the current active tunnel URL
        const match = /var githubOnboardingUrl = "(https:\/\/[^"]+)";/.exec(html);

        if (!match) {
            Logger.log("FAILURE: Could not find tunnel URL in GitHub Pages.");
            sendSovereignEmail("CRITICAL: Redirector Logic Violation", "The githubOnboardingUrl variable is missing from index.html.");
            return;
        }

        const tunnelUrl = match[1];
        Logger.log("Active Tunnel: " + tunnelUrl);

        // 3. Ping the tunnel health endpoint
        const healthUrl = tunnelUrl + "/health";
        const healthRes = UrlFetchApp.fetch(healthUrl, { muteHttpExceptions: true });

        if (healthRes.getResponseCode() !== 200) {
            Logger.log("FAILURE: Tunnel is unreachable or returned error " + healthRes.getResponseCode());
            sendSovereignEmail("OUTAGE: Tunnel Down", "The portal at " + tunnelUrl + " is unreachable.");
            return;
        }

        const healthData = JSON.parse(healthRes.getContentText());
        if (healthData.status === "healthy") {
            Logger.log("AUDIT SUCCESS: Portal is healthy and accurately mapped.");
        } else {
            Logger.log("FAILURE: Portal reported unhealthy state.");
            sendSovereignEmail("INTEGRITY ISSUE: Substandard Health", "The portal responded but reported an unhealthy state.");
        }

    } catch (e) {
        Logger.log("RUNTIME ERROR: " + e.toString());
        sendSovereignEmail("SYSTEM ERROR: Auditor Failure", e.toString());
    }
}

function sendSovereignEmail(subject, body) {
    // Replace with your email or use a service
    const recipient = "gaelf@example.com";
    MailApp.sendEmail(recipient, "[Watchdog] " + subject, body);
}
