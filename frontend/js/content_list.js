/**
 * Content List Management Logic
 * Handles data fetching, inline-editing, and message generation.
 */

const ContentManager = {
    campaigns: [],
    container: document.getElementById('content-list'),
    saveStatus: document.getElementById('save-status'),

    async init() {
        await this.fetchData();
        this.render();
        this.setupEventListeners();
    },

    getContactName(camp) {
        return camp.registry_name || null;
    },

    async fetchData() {
        const isLocalFile = window.location.protocol === 'file:';
        const apiUrl = isLocalFile ? '../data/final_real_growth_list.json' : 'http://localhost:5010/api/growth-list';

        try {
            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            this.campaigns = await response.json();
        } catch (error) {
            console.error('Error fetching growth list:', error);
            let errorMsg = 'Failed to load data.';
            if (isLocalFile) {
                errorMsg = `
                    <div style="background: rgba(255, 75, 43, 0.1); border: 1px solid #FF4B2B; padding: 20px; border-radius: 8px; margin-top: 20px;">
                        <h3 style="color: #FF4B2B; margin-top: 0;">Access Blocked (CORS)</h3>
                        <p>Browsers block local file access for security. Please use the server URL:</p>
                        <code style="background: #000; padding: 10px; display: block; margin: 10px 0; border: 1px solid #333; border-radius: 4px; color: #0f0;">${window.location.origin}/mgmt</code>
                    </div>
                `;
            } else {
                errorMsg = `<p style="color: #FF4B2B; text-align: center;">Server error identified. Please ensure the onboarding server is running and data is present.</p>`;
            }
            this.container.innerHTML = errorMsg;
        }
    },

    getIshmaelIDs() {
        const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];
        const ids = [];
        // Single letters: A-G (Indices 1-7)
        letters.forEach((l, i) => ids.push({ id: l, num: i + 1 }));

        // Double letters: AA-AG, BA-BG [...] GA-GG (Indices 8-56)
        let count = 8;
        for (const l1 of letters) {
            for (const l2 of letters) {
                ids.push({ id: l1 + l2, num: count++ });
            }
        }
        return ids;
    },

    /**
     * Scarcity Resolution: Renders the title as toggleable word tokens.
     * The selected tokens form the 'identity_name'.
     */
    renderTitleTokens(camp) {
        // Split title into English and Arabic parts using '|' as separator
        const parts = camp.title.split('|');
        const englishPart = parts[0].trim();
        const words = englishPart.split(/\s+/).filter(w => w.length > 0);

        // If no selection yet, default to first 2 words if available
        const selectedIndices = camp.identity_indices || (words.length >= 2 ? [0, 1] : (words.length > 0 ? [0] : []));

        if (words.length === 0) {
            return `<span style="color: #666; font-style: italic;">(No English Title)</span>`;
        }

        return words.map((word, idx) => {
            const isSelected = selectedIndices.includes(idx);
            return `
                <button class="word-token ${isSelected ? 'selected' : ''}" 
                        onclick="ContentManager.toggleWord('${camp.bid}', ${idx})"
                        title="Click to include in Trustee Name">
                    ${word}
                </button>
            `;
        }).join(' ');
    },

    toggleWord(bid, idx) {
        const camp = this.campaigns.find(c => c.bid === bid);
        if (!camp) return;

        if (!camp.identity_indices) camp.identity_indices = [0, 1];

        const pos = camp.identity_indices.indexOf(idx);
        if (pos > -1) {
            camp.identity_indices.splice(pos, 1);
        } else {
            camp.identity_indices.push(idx);
        }
        camp.identity_indices.sort((a, b) => a - b);

        // Update the display name
        this.render();
        this.saveToServer();
    },

    getIdentityName(camp) {
        // WhatsApp Registry Name fallback NO LONGER definitive if English title exists

        const parts = camp.title.split('|');
        const englishPart = parts[0].trim();
        const words = englishPart.split(/\s+/).filter(w => w.length > 0);
        const indices = camp.identity_indices || (words.length >= 2 ? [0, 1] : (words.length > 0 ? [0] : []));

        const identity = indices.map(i => words[i]).join(' ').replace(/[^\w\s]/g, '');
        if (identity.trim()) return identity;

        // Fallback to registry name ONLY if no English identity resolved
        if (camp.registry_name) return camp.registry_name;

        return "Trustee";
    },

    render() {
        if (!this.campaigns.length) return;
        this.container.innerHTML = this.campaigns.map(camp => this.createCard(camp)).join('');
    },

    createCard(camp) {
        const isRedundant = camp.whatsapp === "972592640875";
        const cardClass = isRedundant ? 'mgmt-card card-redundant' : 'mgmt-card';
        const redundantBadge = isRedundant ? '<span class="redundant-badge">HUB OVERLAP</span>' : '';
        const ishmaelIDs = this.getIshmaelIDs();
        const activeTrustee = ishmaelIDs.find(i => i.id === camp.ishmael_id);
        const trusteeLabel = activeTrustee ? `Trustee ${activeTrustee.num} (${activeTrustee.id})` : 'Unassigned';

        const identityName = this.getIdentityName(camp);
        const contactName = camp.registry_name;
        const isRegistryLinked = !!contactName;

        const isLive = camp.status === 'live' || !!camp.whydonate_url;
        const statusBadge = isLive ? '<span class="tag" style="background: rgba(50, 191, 85, 0.2); color: #32BF55; border: 1px solid #32BF55; font-weight: bold;">LIVE ON WHYDONATE</span>' : '';

        // Unassessed Check: No English part or Title is numerical
        const isUnassessed = !isLive && !camp.title.includes('|') && (!/[a-zA-Z]/.test(camp.title));
        const unassessedBadge = isUnassessed ? '<span class="tag" style="background: rgba(255, 75, 43, 0.1); color: #FF4B2B; border-color: #FF4B2B;">UNASSESSED</span>' : '';

        return `
            <div class="${cardClass}" data-id="${camp.bid}">
                <img src="${this.resolveImagePath(camp.image, camp.bid)}" class="mgmt-img" alt="Campaign">
                <div class="mgmt-info">
                    <div style="display: flex; align-items: start; justify-content: space-between;">
                        <div style="width: 100%;">
                            <div style="display: flex; align-items: center; margin-bottom: 8px; gap: 8px;">
                                <strong style="color: var(--color-text-dim); font-size: 0.8rem; text-transform: uppercase;">Identity:</strong>
                                <span style="font-weight: bold; color: var(--color-primary);">${identityName}</span>
                                <button class="field-copy" onclick="ContentManager.copyField('${camp.bid || camp.norm_whatsapp}', 'identity', this)">Copy</button>
                                ${statusBadge}
                                ${unassessedBadge}
                            </div>
                            
                            <div style="margin-bottom: 12px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                    <label style="font-size: 0.7rem; color: #666; text-transform: uppercase;">Bilingual Title (English | Arabic)</label>
                                    <button class="field-copy" onclick="ContentManager.copyField('${camp.bid}', 'title', this)">Copy Title</button>
                                </div>
                                <input type="text" class="mgmt-input title-editor" 
                                       style="font-family: inherit; font-weight: bold; padding: 6px 10px;"
                                       value="${camp.title || ''}" 
                                       data-field="title"
                                       placeholder="English Title | Arabic Title">
                            </div>

                            <div class="token-container">
                                ${this.renderTitleTokens(camp)}
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 4px; margin-top: 5px;">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span class="bid">${camp.bid || 'UNIFIED'} ${redundantBadge}</span>
                                    <span class="tag" style="background: rgba(151, 134, 75, 0.2); color: var(--color-primary);">ID: ${trusteeLabel}</span>
                                    ${contactName ? `<span class="tag" style="background: rgba(0, 255, 0, 0.2); color: #0f0; border: 1px solid #0f0; font-weight: bold;">WA IDENTIFIED: ${contactName}</span>` : ''}
                                </div>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    ${(camp.bid && camp.bid.includes('chuffed')) ? `<span class="tag" style="background: rgba(255, 165, 0, 0.1); color: #ffa500; border-color: #ffa500;">PRIORITY: CHUFFED LEAD</span>` : ''}
                                    ${camp.validation_source === 'onboarding_submission' ? `<span class="tag" style="background: rgba(74, 144, 226, 0.1); color: #4A90E2; border-color: #4A90E2;">INTAKE SUBMISSION</span>` : ''}
                                    <button class="field-copy" onclick="ContentManager.copyField('${camp.bid || camp.norm_whatsapp}', 'goal', this)">Copy Goal</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <label style="font-size: 0.7rem; color: #666; text-transform: uppercase;">Campaign Story (Bilingual)</label>
                            <button class="field-copy" onclick="ContentManager.copyField('${camp.bid}', 'description', this)">Copy Description</button>
                        </div>
                        <textarea class="mgmt-input description-editor" 
                                  style="height: 120px; font-size: 0.85rem; background: #0d1117; line-height: 1.4;"
                                  data-field="description"
                                  placeholder="Translate or refine story here...">${camp.description}</textarea>
                    </div>
                    <div class="mgmt-contact">
                        <a href="whatsapp://send?phone=${camp.whatsapp}&text=${encodeURIComponent(ContentManager.generateBilingualMessage(camp))}" class="wa-link">
                            <span class="icon">💬</span> ${camp.whatsapp}
                        </a>
                        <span class="tag">Source: ${camp.validation_source || 'Recovered'}</span>
                    </div>
                </div>
                <div class="mgmt-actions">
                    <div class="mgmt-input-group">
                        <label>WhyDonate URL</label>
                        <input type="text" class="mgmt-input" placeholder="Paste link here..." 
                               value="${camp.whydonate_url || ''}" data-field="whydonate_url">
                    </div>
                    <div class="mgmt-input-group">
                        <label>Trustee Assignment</label>
                        <select class="mgmt-input" data-field="ishmael_id">
                            <option value="">-- Unassigned --</option>
                            ${ishmaelIDs.map(i => `<option value="${i.id}" ${camp.ishmael_id === i.id ? 'selected' : ''}>${i.num}: Trustee ${i.id}</option>`).join('')}
                        </select>
                    </div>
                    <div class="mgmt-input-group">
                        <label>Status</label>
                        <select class="mgmt-input" data-field="status">
                            <option value="pending" ${camp.status === 'pending' ? 'selected' : ''}>Pending</option>
                            <option value="verified" ${camp.status === 'verified' ? 'selected' : ''}>Verified</option>
                            <option value="live" ${camp.status === 'live' ? 'selected' : ''}>Live</option>
                            <option value="redundant" ${camp.status === 'redundant' ? 'selected' : ''}>Redundant</option>
                        </select>
                    </div>
                    <button class="copy-btn" onclick="ContentManager.copyOnboardingMessage('${camp.bid || camp.norm_whatsapp}')">
                        Copy Message
                    </button>
                </div>
            </div>
        `;
    },

    resolveImagePath(path, bid) {
        if (!path) return 'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&q=80&w=200';
        return path.replace(/.*local_ai_campaign_assistant/, '..').replace(/\\/g, '/');
    },

    setupEventListeners() {
        this.container.addEventListener('blur', (e) => {
            if (e.target.classList.contains('editable')) {
                const id = e.target.closest('.mgmt-card').dataset.id;
                const field = e.target.dataset.field;
                const value = e.target.innerText;
                this.updateLocalData(id, field, value);
            }
        }, true);

        this.container.addEventListener('change', (e) => {
            if (e.target.classList.contains('mgmt-input')) {
                const id = e.target.closest('.mgmt-card').dataset.id;
                const field = e.target.dataset.field;
                const value = e.target.value;
                this.updateLocalData(id, field, value);
            }
        });

        document.getElementById('search-input').addEventListener('input', () => this.applyFilters());
        document.getElementById('status-filter').addEventListener('change', () => this.applyFilters());
    },

    applyFilters() {
        const query = document.getElementById('search-input').value.toLowerCase();
        const status = document.getElementById('status-filter').value;
        const cards = document.querySelectorAll('.mgmt-card');

        cards.forEach(card => {
            const id = card.dataset.id;
            const camp = this.campaigns.find(c => c.bid === id || c.norm_whatsapp === id);
            if (!camp) return;

            const textMatch = card.innerText.toLowerCase().includes(query);
            const statusMatch = (status === 'all') ||
                (status === 'live' && (camp.status === 'live' || !!camp.whydonate_url)) ||
                (status === camp.status);

            card.style.display = (textMatch && statusMatch) ? 'grid' : 'none';
        });
    },

    async updateLocalData(id, field, value) {
        const camp = this.campaigns.find(c => c.bid === id);
        if (camp) {
            camp[field] = value;
            console.log(`Updated ${id} field ${field} to:`, value);

            // Re-render only important parts if needed
            // For real-time token generation, we need to re-render if title changes
            if (field === 'title' || field === 'ishmael_id' || field === 'identity_indices') {
                this.render();
                // Focusing back is tricky, but let's try for simple flow
                const activeField = document.querySelector(`[data-id="${id}"] .${field}-editor`);
                if (activeField) {
                    activeField.focus();
                    // Set cursor to end
                    const len = activeField.value.length;
                    activeField.setSelectionRange(len, len);
                }
            }

            await this.saveToServer();
            this.showSaveIndicator();
        }
    },

    copyField(bid, field, btn) {
        const camp = this.campaigns.find(c => c.bid === bid);
        if (!camp) return;

        let text = "";
        if (field === 'identity') text = this.getIdentityName(camp);
        else if (field === 'title') text = camp.title;
        else if (field === 'description') text = camp.description;
        else if (field === 'goal') text = camp.goal || "5000";

        navigator.clipboard.writeText(text).then(() => {
            const originalText = btn.innerText;
            btn.innerText = 'COPIED!';
            btn.style.color = '#0f0';
            setTimeout(() => {
                btn.innerText = originalText;
                btn.style.color = '';
            }, 1000);
        });
    },

    async saveToServer() {
        try {
            const response = await fetch('http://localhost:5010/api/growth-list-save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.campaigns)
            });
            if (!response.ok) throw new Error('Save failed');
            console.log('Successfully saved to server');
        } catch (error) {
            console.error('Error saving to server:', error);
            alert('Failed to save changes to server. Please check your connection.');
        }
    },

    showSaveIndicator() {
        this.saveStatus.innerText = '✓ Saved to Sovereign Registry';
        this.saveStatus.style.display = 'block';
        clearTimeout(this.saveTimer);
        this.saveTimer = setTimeout(() => {
            this.saveStatus.style.display = 'none';
        }, 2000);
    },

    copyOnboardingMessage(id) {
        const camp = this.campaigns.find(c => c.bid === id);
        if (!camp) return;

        const message = this.generateBilingualMessage(camp);
        navigator.clipboard.writeText(message).then(() => {
            const btn = document.querySelector(`[data-id="${id}"] .copy-btn`);
            const originalText = btn.innerText;
            btn.innerText = 'Copied!';
            btn.classList.add('success');
            setTimeout(() => {
                btn.innerText = originalText;
                btn.classList.remove('success');
            }, 2000);
        });
    },

    generateBilingualMessage(camp) {
        const ishmaelIDs = this.getIshmaelIDs();
        const activeTrustee = ishmaelIDs.find(i => i.id === camp.ishmael_id);
        const shortID = activeTrustee ? `${activeTrustee.id}#${activeTrustee.num}` : 'Pending';
        const identity = this.getIdentityName(camp);

        return `Salam, ${identity} (ID: ${shortID})\n\nThis is your onboarding link: ${camp.whydonate_url || '[PENDING LINK]'}\n\n---\n\nسلام ، ${identity} (ID: ${shortID})\n\nهذا هو رابط الانضمام الخاص بك: ${camp.whydonate_url || '[رابط معلق]'}`;
    }
};

document.addEventListener('DOMContentLoaded', () => ContentManager.init());
