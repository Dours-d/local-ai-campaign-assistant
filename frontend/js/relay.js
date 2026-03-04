/**
 * FAJR RELAY SYSTEM
 * Manages campaign links and provides failover to the General Trust Fund.
 */

const RELAY_FUND_URL = "https://whydonate.com/fundraising/help-fajrtoday-the-first-crypto-utility-providing-critical-services";

// In a real deployment, this would be fetched from a dynamic endpoint (e.g., status.json)
let CAMPAIGN_STATUS = {
    // "id": "OFFLINE" | "ACTIVE"
};

/**
 * Perform a redirected gift based on health status.
 * @param {string} campaignId - The unique identifier for the campaign.
 * @param {string} primaryUrl - The direct WhyDonate URL.
 * @param {string} displayName - Human-readable name for instructions.
 */
function initiateRelayGift(campaignId, primaryUrl, displayName) {
    const status = CAMPAIGN_STATUS[campaignId] || "ACTIVE";

    if (status === "ACTIVE") {
        // Normal path
        window.open(primaryUrl, '_blank');
    } else {
        // Relay path
        console.warn(`Relaying the Amanah for ${displayName} through the Sovereign fund.`);

        // Show instruction modal or alert before redirecting
        const confirmRelay = confirm(
            `SOVEREIGN RELAY: The platform link for "${displayName}" has been interrupted, but the human relationship (Amanah) remains unbroken. \n\n` +
            `We are now relaying your support through the General Trust fund to ensure your gift reaches its destination. \n\n` +
            `IMPORTANT: To preserve the specific aim of your gift, please write "${displayName}" in the donation comments on the next page. \n\n` +
            `Click OK to fulfill the Trust through the relay fund.`
        );

        if (confirmRelay) {
            window.open(RELAY_FUND_URL, '_blank');
        }
    }
}

/**
 * Optional: Check a specialized status.json to update known local/offline status.
 */
async function syncRelayStatus() {
    try {
        const response = await fetch('data/campaign_status.json');
        if (response.ok) {
            const remoteStatus = await response.json();
            CAMPAIGN_STATUS = { ...CAMPAIGN_STATUS, ...remoteStatus };
            console.log("Relay status synced with registry.");
            updateUIBadges();
        }
    } catch (e) {
        console.log("No remote relay status found. Using defaults.");
    }
}

/**
 * Updates campaign card badges based on the synced trust status.
 */
function updateUIBadges() {
    for (const [id, status] of Object.entries(CAMPAIGN_STATUS)) {
        const badge = document.querySelector(`.card-status[data-campaign-id="${id}"]`);
        if (badge) {
            if (status === "ACTIVE") {
                badge.innerHTML = '<span class="status-dot active"></span> TRUST VERIFIED';
                badge.classList.remove('relayed');
            } else {
                badge.innerHTML = '<span class="status-dot relayed"></span> RELAY ACTIVE';
                badge.classList.add('relayed');
            }
        }
    }
}

// Initial sync on load
syncRelayStatus();

/**
 * Opens the Noor AI tunnel (brain.html).
 * Uses the dynamic status.json resolver for resilience.
 */
async function openShahada() {
    // Priority 1: Use the targetUrl synchronized by the watchdog
    if (typeof targetUrl !== 'undefined' && targetUrl && targetUrl.startsWith('http')) {
        const baseUrl = targetUrl.endsWith('/') ? targetUrl.slice(0, -1) : targetUrl;
        window.open(baseUrl + '/brain' + window.location.search, '_blank');
        return;
    }

    // Priority 2: Use the dynamic status.json resolver
    try {
        const response = await fetch('https://fajr.today/data/status.json?t=' + Date.now());
        if (response.ok) {
            const status = await response.json();
            const url = status.services.brain_portal.public_url;
            window.open(url, '_blank');
            return;
        }
    } catch (e) {
        console.warn("Dynamic resolver failed, falling back to cached URL.");
    }
    window.open('https://dours-d.github.io/local-ai-campaign-assistant/brain.html', '_blank');
}

/**
 * Opens the Onboarding Form.
 * Uses the dynamic status.json resolver for resilience.
 */
async function openOnboarding() {
    // Priority 1: Use the targetUrl synchronized by the watchdog
    if (typeof targetUrl !== 'undefined' && targetUrl && targetUrl.startsWith('http')) {
        const baseUrl = targetUrl.endsWith('/') ? targetUrl.slice(0, -1) : targetUrl;
        window.open(baseUrl + '/onboard' + window.location.search, '_blank');
        return;
    }

    try {
        const response = await fetch('https://fajr.today/data/status.json?t=' + Date.now());
        if (response.ok) {
            const status = await response.json();
            const url = status.services.shahada_portal.public_url;
            window.open(url, '_blank');
            return;
        }
    } catch (e) {
        console.warn("Dynamic resolver failed for onboarding, falling back to cached URL.");
    }
    // Final fallback: Use the root-level redirector on GitHub Pages
    window.open('https://dours-d.github.io/local-ai-campaign-assistant/onboard.html', '_blank');
}

/**
 * Sacred Ritual: Opens the Shahada visual modal.
 */
function openShahadaModal() {
    const modal = document.querySelector('.shahada-modal-overlay');
    if (modal) {
        modal.classList.add('open');
    } else {
        console.error("Shahada modal not found in DOM.");
    }
}

/**
 * Closes the Shahada visual modal.
 */
function closeShahadaModal() {
    const modal = document.querySelector('.shahada-modal-overlay');
    if (modal) {
        modal.classList.remove('open');
    }
}
