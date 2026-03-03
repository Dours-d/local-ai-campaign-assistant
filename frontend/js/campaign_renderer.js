/**
 * Simple Campaign Renderer for Fajr Today
 * Fetches registry.json and renders campaign cards dynamically.
 */
class CampaignRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.registryPath = 'assets/registry.json';
        this.assetsPath = 'assets/campaigns/';
    }

    async init() {
        if (!this.container) return;

        try {
            const response = await fetch(`${this.registryPath}?v=${Date.now()}`);
            if (!response.ok) throw new Error('Failed to load registry');
            const campaigns = await response.json();
            this.render(campaigns);
        } catch (error) {
            console.error('Renderer Error:', error);
            this.container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; opacity: 0.5;">Field data temporarily unavailable.</p>';
        }
    }

    render(campaigns) {
        this.container.innerHTML = '';

        campaigns.forEach((camp, index) => {
            const card = this.createCard(camp, index);
            this.container.appendChild(card);
        });

        // Initialize AOS if available
        if (window.AOS) {
            window.AOS.refresh();
        }
    }

    createCard(camp, index) {
        const div = document.createElement('div');
        div.className = 'card';
        div.setAttribute('data-aos', 'fade-up');
        div.setAttribute('data-aos-delay', (index % 3) * 100);

        const identity = camp.custom_identity_name || camp.title || "Sovereign Soul";
        const ishmaelId = camp.ishmael_id || "???";
        let story = camp.story || camp.description || "Witnessing resilience on the ground.";
        if (story.length > 200) story = story.substring(0, 197) + "...";

        // Handle Image
        const imgName = camp.image ? camp.image.split(/[\\/]/).pop() : '';
        const imgSrc = imgName ? `${this.assetsPath}${imgName}` : null;

        const imgHtml = imgSrc
            ? `<img src="${imgSrc}" class="card-img" alt="${identity}" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\'card-image-fallback\'>${ishmaelId}</div>'">`
            : `<div class="card-image-fallback">${ishmaelId}</div>`;

        // Handle Bilingual Title
        let titleAr = "";
        let titleEn = identity;
        if (identity.includes('|')) {
            const parts = identity.split('|').map(p => p.trim());
            titleEn = parts[0];
            titleAr = parts[1];
        }

        const url = camp.whydonate_url || "#";
        const encodedUrl = encodeURIComponent(url);
        const tweetText = encodeURIComponent(`Support ${titleEn}: `);
        const spreadLink = `https://twitter.com/intent/tweet?text=${tweetText}&url=${encodedUrl}`;

        div.innerHTML = `
            <div class="card-status" data-campaign-id="${camp.norm_whatsapp || index}">
                <span class="status-dot active"></span> TRUST VERIFIED
            </div>
            ${imgHtml}
            <div class="card-body" style="padding: 1.5rem; display: flex; flex-direction: column; flex-grow: 1;">
                <h3 class="lang-dual" style="margin-bottom: 1rem;">
                    <span class="ar-main">${titleAr}</span>
                    <span class="en-sub">${titleEn}</span>
                </h3>
                <p style="font-size: 0.95rem; opacity: 0.8; margin-bottom: 1.5rem; flex-grow: 1;">${story}</p>
                <div class="card-actions" style="display: flex; gap: 1rem; margin-top: auto;">
                    <a href="${url}" target="_blank" class="btn btn-primary" style="flex: 1; text-align: center;">DIRECT GIFT</a>
                    <a href="${spreadLink}" target="_blank" class="btn btn-outline" style="flex: 1; text-align: center; border: 1px solid rgba(255,255,255,0.1); padding: 0.6rem; border-radius: 8px; text-decoration: none; color: white; font-size: 0.9rem;">SPREAD</a>
                </div>
            </div>
        `;
        return div;
    }
}

// Global Init
document.addEventListener('DOMContentLoaded', () => {
    const renderer = new CampaignRenderer('campaign-list-container');
    renderer.init();
});
