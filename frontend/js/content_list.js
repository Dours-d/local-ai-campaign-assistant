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
        await this.fetchTemplate();
        await this.normalizeCampaigns();
        this.render();
        this.setupEventListeners();

        // Start background automation
        this.autoCompleteBilingual();
    },

    async fetchTemplate() {
        try {
            console.log('Fetching onboarding template with cache-buster...');
            const apiBase = window.location.port === '4040' ? 'http://127.0.0.1:5010' : '';
            const resp = await fetch(`${apiBase}/api/onboarding-template?v=${Date.now()}`);
            if (resp.ok) {
                this.onboardingTemplate = await resp.text();
                console.log('✅ Onboarding template loaded successfully. Length:', this.onboardingTemplate.length);
            } else {
                console.error('❌ Failed to load onboarding template. Status:', resp.status);
            }
        } catch (e) {
            console.error('❌ Error fetching onboarding template:', e);
        }
    },

    async normalizeCampaigns() {
        let changed = false;
        this.campaigns.forEach(camp => {
            if (camp.title && camp.title.includes('|')) {
                const parts = camp.title.split('|').map(p => p.trim());
                if (parts.length >= 2) {
                    const p1_ar = /[\u0600-\u06FF]/.test(parts[0]);
                    const p2_ar = /[\u0600-\u06FF]/.test(parts[1]);
                    // If Arabic is on the left, but Right is English/Mixed, flip it
                    if (p1_ar && !p2_ar) {
                        camp.title = `${parts[1]} | ${parts[0]}`;
                        changed = true;
                    }
                }
            }
        });
        if (changed) {
            console.log('Bilingual ordering normalized. Saving to registry...');
            await this.saveToServer();
        }
    },

    async autoCompleteBilingual() {
        console.log('--- STARTING AUTOMATED BILINGUAL COMPLETION ---');
        let count = 0;
        console.log(`Analyzing ${this.campaigns.length} campaigns...`);

        for (const camp of this.campaigns) {
            const id = camp.norm_whatsapp || camp.bid || camp.bids?.[0];
            if (!id) continue;

            // Check title
            const needsTitle = this.needsTranslation(camp.title, 'title');
            if (needsTitle) {
                console.log(`Auto-translating title for ${id}...`);
                await this.translateFieldSilent(id, 'title');
                count++;
                await new Promise(r => setTimeout(r, 1000)); // Rate limit buffer
            }

            // Check description
            const needsDesc = this.needsTranslation(camp.description, 'description');
            if (needsDesc) {
                console.log(`Auto-translating description for ${id}...`);
                await this.translateFieldSilent(id, 'description');
                count++;
                await new Promise(r => setTimeout(r, 1000)); // Rate limit buffer
            }
        }

        if (count > 0) {
            console.log(`Background automation completed ${count} translations.`);
        }
    },

    needsTranslation(text, mode) {
        const val = (text || '').trim();
        if (!val) return false;
        if (mode === 'title') {
            // Needs translation if it doesn't contain a pipe or if one side is missing
            if (!text.includes('|')) return true;
            const parts = text.split('|').map(p => p.trim());
            return parts.length < 2 || !parts[0] || !parts[1];
        } else {
            // Needs translation if it doesn't contain the separator
            return !text.includes('---');
        }
    },

    async translateFieldSilent(id, field) {
        const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || c.bids?.[0]) === id);
        if (!camp) return;

        const text = camp[field] || '';
        const apiBase = window.location.port === '4040' ? 'http://127.0.0.1:5010' : '';
        try {
            const resp = await fetch(`${apiBase}/api/translate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, mode: field })
            });
            const data = await resp.json();
            if (data.error) throw new Error(data.error);

            const bilingual = data.bilingual || `${data.translation} | ${text}`;

            // Update local data and save
            camp[field] = bilingual;
            await this.saveToServer();

            // Surgical UI update
            const cardEl = document.querySelector(`.mgmt-card[data-id="${CSS.escape(id)}"]`);
            if (cardEl) {
                if (field === 'title') {
                    const inp = cardEl.querySelector('.title-editor');
                    if (inp) {
                        inp.value = bilingual;
                        this.handleTitleInput(inp);
                    }
                    const identitySpan = cardEl.querySelector('[data-identity-label]');
                    if (identitySpan) identitySpan.textContent = this.getIdentityName(camp);
                    const tc = cardEl.querySelector('.token-container');
                    if (tc) tc.innerHTML = this.renderTitleTokens(camp, id);
                } else {
                    const ta = cardEl.querySelector('.description-editor');
                    if (ta) ta.value = bilingual;
                }
            }
        } catch (err) {
            console.error(`Silent auto-translation failed for ${id}:`, err);
        }
    },

    getContactName(camp) {
        return camp.registry_name || null;
    },

    async fetchData() {
        const isLocalFile = window.location.protocol === 'file:';
        const apiBase = window.location.port === '4040' ? 'http://127.0.0.1:5010' : '';
        const apiUrl = isLocalFile ? '../data/final_real_growth_list.json' : `${apiBase}/api/growth-list`;

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


    getCharClass(len) {
        if (len > 75) return 'danger';
        if (len > 65) return 'warning';
        return 'ok';
    },

    handleTitleInput(input) {
        const bid = input.dataset.bid;
        const len = input.value.length;
        const countEl = document.querySelector(`[data-char-count="${bid}"]`);
        if (countEl) {
            countEl.textContent = `${len}/75`;
            countEl.className = `char-count ${this.getCharClass(len)}`;
        }
    },

    /**
     * Scarcity Resolution: Renders the title as toggleable word tokens.
     * The selected tokens form the 'identity_name'.
     */
    renderTitleTokens(camp, campKey) {
        campKey = campKey || camp.norm_whatsapp || camp.bids?.[0];
        const ishmaelIDs = this.getIshmaelIDs();
        const activeTrustee = ishmaelIDs.find(i => i.id === camp.ishmael_id);
        const letterCode = camp.ishmael_id || '?';
        const letterNum = activeTrustee ? activeTrustee.num : '–';

        // Split title into English and Arabic parts using '|' as separator
        const parts = camp.title.split('|');
        const englishPart = parts[0].trim();
        const words = englishPart.split(/\s+/).filter(w => w.length > 0);

        // If no selection yet, default to first 2 words if available
        const selectedIndices = camp.identity_indices || (words.length >= 2 ? [0, 1] : (words.length > 0 ? [0] : []));

        const tokenHTML = words.length === 0
            ? `<span style="color: #666; font-style: italic;">(No English Title)</span>`
            : words.map((word, idx) => {
                const isSelected = selectedIndices.includes(idx);
                return `<button class="word-token ${isSelected ? 'selected' : ''}" 
                        onclick="ContentManager.toggleWord('${campKey}', ${idx})"
                        title="Click to include in Trustee Name">${word}</button>`;
            }).join(' ');

        const isNamed = this.isNamedIdentity(camp);
        const ishmaelBadge = isNamed ? `
                <div class="ishmael-badge" data-key="${campKey}" title="Trustee Letter Code"
                     onclick="ContentManager.cycleIshmaelID('${campKey}')">
                    ${letterCode}
                </div>
                <span style="color:#666; font-size:0.75rem;">#${letterNum}</span>` : '';

        return `
            <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                <div style="display:flex; gap:6px; flex-wrap:wrap; align-items:center;">${tokenHTML}</div>
                ${ishmaelBadge}
            </div>`;
    },

    toggleWord(bid, idx) {
        const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || c.bids?.[0]) === bid);
        if (!camp) return;

        if (!camp.identity_indices) camp.identity_indices = [0, 1];

        const pos = camp.identity_indices.indexOf(idx);
        if (pos > -1) {
            camp.identity_indices.splice(pos, 1);
        } else {
            camp.identity_indices.push(idx);
        }
        camp.identity_indices.sort((a, b) => a - b);

        // Manual Override: Ishmael ID is a manual discriminator chosen by the user.
        // It should NOT be automatically edited or calculated by the code.

        // Surgical patch — update just this card's token area
        const card = document.querySelector(`.mgmt-card[data-id="${CSS.escape(bid)}"]`);
        if (card) {
            const tokenContainer = card.querySelector('.token-container');
            if (tokenContainer) tokenContainer.innerHTML = this.renderTitleTokens(camp, bid);

            const identitySpan = card.querySelector('[data-identity-label]');
            if (identitySpan) identitySpan.textContent = this.getIdentityName(camp);
        }

        this.saveToServer();
    },

    cycleIshmaelID(bid) {
        const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || c.bids?.[0]) === bid);
        if (!camp) return;

        const allIDs = this.getIshmaelIDs();
        const currentIdx = allIDs.findIndex(i => i.id === camp.ishmael_id);

        // Purely local cycle: Just move to the next ID in the sequence.
        const nextIdx = (currentIdx + 1) % allIDs.length;
        const next = allIDs[nextIdx];
        if (!next) return;

        camp.ishmael_id = next.id;
        this.refreshAllIshmaelSelects();

        // Patch badge
        const card = document.querySelector(`.mgmt-card[data-id="${CSS.escape(bid)}"]`);
        if (card) {
            const tokenContainer = card.querySelector('.token-container');
            if (tokenContainer) tokenContainer.innerHTML = this.renderTitleTokens(camp, bid);
            const identityLabel = card.querySelector('[data-identity-label]');
            if (identityLabel) identityLabel.textContent = this.getDisplayName(camp);
        }

        this.saveToServer();
    },

    syncIshmaelBadge(bid, newId) {
        const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || c.bids?.[0]) === bid);
        if (!camp) return;

        // Manual Selection: Update ONLY this specific campaign.
        // NO propagation to other homonymous cards.
        camp.ishmael_id = newId || null;

        // Refresh badge/tokens for this card
        const card = document.querySelector(`.mgmt-card[data-id="${CSS.escape(bid)}"]`);
        if (card) {
            const tokenContainer = card.querySelector('.token-container');
            if (tokenContainer) tokenContainer.innerHTML = this.renderTitleTokens(camp, bid);
            const select = card.querySelector('[data-ishmael-select]');
            if (select) select.value = camp.ishmael_id || '';
            const identityLabel = card.querySelector('[data-identity-label]');
            if (identityLabel) identityLabel.textContent = this.getDisplayName(camp);
        }

        this.saveToServer();
    },

    renderIshmaelOptions(camp) {
        const allIDs = this.getIshmaelIDs();
        const current = camp.ishmael_id || '';

        let html = '<option value="">-- Unassigned --</option>';
        allIDs.forEach(i => {
            // Pure manual selection: No more "Taken by" or disabling.
            html += `<option value="${i.id}" ${current === i.id ? 'selected' : ''}>${i.id}</option>`;
        });
        return html;
    },

    refreshAllIshmaelSelects() {
        this.campaigns.forEach(camp => {
            const bid = camp.norm_whatsapp || camp.bid || camp.bids?.[0];
            const select = document.querySelector(`.mgmt-card[data-id="${CSS.escape(bid)}"] [data-ishmael-select]`);
            if (select) {
                select.innerHTML = this.renderIshmaelOptions(camp);
            }
        });
        console.log('--- Ishmael Selects Unified & Refreshed ---');
    },

    getIdentityName(camp) {
        // Priority 1: User Manual Override (highest precedence)
        // If the user manually typed an identity, it overrides EVERYTHING (tokens and letter)
        if (camp.manual_identity && camp.manual_identity.trim().length > 0) {
            return camp.manual_identity.trim();
        }

        // Priority 2: Calculated Identity (Tokens or Phone) + Letter
        // If the manual field is virgin, we edit with token and letters
        let basePart = "";
        if (camp.title) {
            const parts = camp.title.split('|').map(p => p.trim());
            const englishPart = parts[0];

            // Handle URLs in title
            if (englishPart.toLowerCase().startsWith('http')) {
                const slug = englishPart.split('/').pop().split('?')[0].replace(/[-_]/g, ' ');
                if (slug && isNaN(slug)) {
                    basePart = slug.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                } else {
                    basePart = englishPart;
                }
            } else {
                const words = englishPart.split(/\s+/).filter(w => w.length > 0);
                const indices = camp.identity_indices || (words.length >= 2 ? [0, 1] : (words.length > 0 ? [0] : []));
                basePart = indices.map(i => words[i]).filter(Boolean).join(' ').replace(/[^\w\s\u0600-\u06FF]/g, '').trim();
            }
        }

        // Fallback: use phone if token-based calculation failed
        if (!basePart) {
            basePart = camp.norm_whatsapp || camp.bid || camp.whatsapp || "";
        }

        const letter = camp.ishmael_id || "";
        return `${basePart}${letter ? ' ' + letter : ''}`.trim();
    },

    getDisplayName(camp) {
        const id = this.getIdentityName(camp);
        if (!id) return '(Unidentified)';
        return id;
    },

    // True only when identity is a real name, not a provisional phone number
    isNamedIdentity(camp) {
        const parts = (camp.title || '').split('|');
        const englishPart = parts[0].trim();
        const words = englishPart.split(/\s+/).filter(w => w.length > 0);
        const indices = camp.identity_indices || (words.length >= 2 ? [0, 1] : (words.length > 0 ? [0] : []));
        const fromTitle = indices.map(i => words[i]).filter(Boolean).join(' ').replace(/[^\w\s\u0600-\u06FF]/g, '').trim();
        if (fromTitle) return true;
        // registry_name is a real name only if it contains letters
        const reg = (camp.registry_name || '').trim();
        return reg.length > 0 && /[a-zA-Z\u0600-\u06FF]/.test(reg);
    },

    render() {
        if (!this.campaigns.length) return;
        this.container.innerHTML = this.campaigns.map(camp => this.createCard(camp)).join('');
    },

    createCard(camp) {
        const campKey = camp.norm_whatsapp || camp.bid || camp.bids?.[0] || 'unknown';
        const primaryBid = camp.bids?.[0] || campKey;
        const isRedundant = camp.whatsapp === "972592640875";
        const identityName = this.getDisplayName(camp);
        const isTrust = identityName === 'Help fajrtoday';
        const cardClass = `mgmt-card ${isRedundant ? 'card-redundant' : ''} ${isTrust ? 'card-trust' : ''}`.trim();
        const redundantBadge = isRedundant ? '<span class="redundant-badge">HUB OVERLAP</span>' : '';
        const sovereignBadge = isTrust ? '<span class="special-badge">SOVEREIGN</span>' : '';

        const ishmaelIDs = this.getIshmaelIDs();
        const activeTrustee = ishmaelIDs.find(i => i.id === camp.ishmael_id);
        const trusteeLabel = activeTrustee ? activeTrustee.id : null;
        const contactName = camp.registry_name;
        const isRegistryLinked = !!contactName;

        const isLive = camp.status === 'live' || !!camp.whydonate_url;
        const statusBadge = isLive ? '<span class="tag" style="background: rgba(50, 191, 85, 0.2); color: #32BF55; border: 1px solid #32BF55; font-weight: bold;">LIVE ON WHYDONATE</span>' : '';

        // Unassessed Check: No English part or Title is numerical
        const isUnassessed = !isLive && !camp.title.includes('|') && (!/[a-zA-Z]/.test(camp.title));
        const unassessedBadge = isUnassessed ? '<span class="tag" style="background: rgba(255, 75, 43, 0.1); color: #FF4B2B; border-color: #FF4B2B;">UNASSESSED</span>' : '';

        return `
            <div class="${cardClass}" data-id="${campKey}">
                <img src="${this.resolveImagePath(camp.image, camp.bid)}" class="mgmt-img" alt="Campaign"
                     style="cursor:pointer; ${camp.marked_for_erasure ? 'opacity:0.35; filter:grayscale(1);' : ''}"
                     onclick="ContentManager.openImageViewer('${campKey}')">
                <div class="mgmt-info">
                    <div style="display: flex; align-items: start; justify-content: space-between;">
                        <div style="width: 100%;">
                            <div style="display: flex; align-items: center; margin-bottom: 8px; gap: 8px;">
                                <strong style="color: var(--color-text-dim); font-size: 0.8rem; text-transform: uppercase;">Identity:</strong>
                                <span style="font-weight: bold; color: var(--color-primary);" data-identity-label>${identityName}</span>
                                <button class="field-copy" onclick="ContentManager.copyField('${campKey}', 'identity', this)">Copy</button>
                                ${statusBadge}
                                ${unassessedBadge}
                                ${sovereignBadge}
                            </div>
                            <div style="margin-bottom: 12px;">
                                <label style="font-size: 0.7rem; color: #666; text-transform: uppercase;">Manual Identity Override (Overrides Tokens + Letter)</label>
                                <input type="text" class="mgmt-input" 
                                       style="padding: 4px 8px; font-size: 0.85rem;"
                                       value="${camp.manual_identity || ''}" 
                                       data-field="manual_identity"
                                       placeholder="Start typing to override Tokens and Letter...">
                            </div>
                            
                            <div style="margin-bottom: 12px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                    <div style="display:flex; align-items:center;">
                                        <label style="font-size: 0.7rem; color: #666; text-transform: uppercase;">Bilingual Title (English | Arabic)</label>
                                        <span class="char-count ${this.getCharClass((camp.title || '').length)}" data-char-count="${campKey}">
                                            ${(camp.title || '').length}/75
                                        </span>
                                    </div>
                                    <div style="display:flex; gap:6px;">
                                        <button class="field-copy" style="color:#4A90E2; border-color:#4A90E2;" onclick="ContentManager.translateField('${campKey}', 'title', this)">🌐 Translate</button>
                                        <button class="field-copy" onclick="ContentManager.copyField('${campKey}', 'title', this)">Copy Title</button>
                                    </div>
                                </div>
                                <input type="text" class="mgmt-input title-editor" 
                                       style="font-family: inherit; font-weight: bold; padding: 6px 10px;"
                                       value="${camp.title || ''}" 
                                       data-field="title"
                                       data-bid="${campKey}"
                                       maxlength="75"
                                       oninput="ContentManager.handleTitleInput(this)"
                                       placeholder="English Title | Arabic Title">
                            </div>

                            <div class="token-container">
                                ${this.renderTitleTokens(camp, campKey)}
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 4px; margin-top: 5px;">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span class="bid">${primaryBid} ${redundantBadge}</span>
                                    ${trusteeLabel ? `<span class="tag" style="background: rgba(151, 134, 75, 0.2); color: var(--color-primary);">${trusteeLabel}</span>` : ''}
                                    ${contactName ? `<span class="tag" style="background: rgba(0, 255, 0, 0.2); color: #0f0; border: 1px solid #0f0; font-weight: bold;">WA IDENTIFIED: ${contactName}</span>` : ''}
                                </div>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    ${(camp.bid && camp.bid.includes('chuffed')) ? `<span class="tag" style="background: rgba(255, 165, 0, 0.1); color: #ffa500; border-color: #ffa500;">PRIORITY: CHUFFED LEAD</span>` : ''}
                                    ${camp.validation_source === 'onboarding_submission' ? `<span class="tag" style="background: rgba(74, 144, 226, 0.1); color: #4A90E2; border-color: #4A90E2;">INTAKE SUBMISSION</span>` : ''}
                                    <button class="fetch-btn" onclick="ContentManager.toggleSubmissions('${campKey}', this)">
                                        🔍 Fetch Submissions
                                    </button>
                                    <button class="field-copy" onclick="ContentManager.copyField('${campKey}', 'goal', this)">Copy Goal</button>
                                </div>
                            </div>

                            <!-- Submissions Dropdown Panel -->
                            <div id="subs-${campKey}" class="submissions-panel">
                                <div class="submissions-title">
                                    <span>Recent Submissions</span>
                                    <button class="field-copy" style="font-size: 0.6rem; padding: 2px 5px;" onclick="ContentManager.toggleSubmissions('${campKey}')">Close</button>
                                </div>
                                <div class="subs-content">
                                    <p style="color: #666; font-size: 0.8rem; font-style: italic;">Fetching assets...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <label style="font-size: 0.7rem; color: #666; text-transform: uppercase;">Campaign Story (Bilingual)</label>
                            <div style="display:flex; gap:6px;">
                                <button class="field-copy" style="color:#4A90E2; border-color:#4A90E2;" onclick="ContentManager.translateField('${campKey}', 'description', this)">🌐 Translate</button>
                                <button class="field-copy" onclick="ContentManager.copyField('${campKey}', 'description', this)">Copy Description</button>
                            </div>
                        </div>
                        <textarea class="mgmt-input description-editor" 
                                  style="height: 120px; font-size: 0.85rem; background: #0d1117; line-height: 1.4;"
                                  data-field="description"
                                  placeholder="Translate or refine story here...">${camp.description}</textarea>
                    </div>
                    <div style="margin-top: 10px;">
                        <label style="font-size: 0.7rem; color: #b8860b; text-transform: uppercase; letter-spacing: 0.5px;">⚑ Notes / Flags</label>
                        <textarea class="mgmt-input" 
                                  style="height: 50px; font-size: 0.82rem; background: rgba(184,134,11,0.05); 
                                         border-color: rgba(184,134,11,0.3); color: #d4a017; margin-top: 4px; line-height: 1.4;"
                                  data-field="notes"
                                  placeholder="e.g. Description mentions Mahmoud but identity is Mohamed — needs review">${camp.notes || ''}</textarea>
                    </div>
                    <div class="mgmt-contact">
                        ${(() => {
                const raw = (camp.whatsapp || '');
                const digits = raw.replace(/\D/g, '');
                // Incomplete if < 10 digits OR starts with 0 (local trunk format)
                const isIncomplete = digits.length < 10 || digits.startsWith('0');
                const baseDigits = digits.startsWith('0') ? digits.slice(1) : digits;
                const fullPhone = (camp.whatsapp_prefix || '') + baseDigits;
                const prefixField = isIncomplete ? `
                                <div style="display:flex; align-items:center; gap:6px; margin-bottom:6px; flex-wrap:wrap;">
                                    <span style="font-size:0.7rem; color:#b8860b; text-transform:uppercase;">⚠ Prefix:</span>
                                    <button onclick="ContentManager.setPrefix('${campKey}', '970', this)"
                                            style="padding:2px 8px; border-radius:4px; cursor:pointer; font-size:0.8rem; transition:all 0.15s;
                                                   ${(camp.whatsapp_prefix === '970') ? 'background:#1a4a2e; border:1px solid #32BF55; color:#32BF55; font-weight:bold;' : 'background:transparent; border:1px solid #555; color:#888;'}">
                                        970 🇵🇸
                                    </button>
                                    <button onclick="ContentManager.setPrefix('${campKey}', '972', this)"
                                            style="padding:2px 8px; border-radius:4px; cursor:pointer; font-size:0.8rem; transition:all 0.15s;
                                                   ${(camp.whatsapp_prefix === '972') ? 'background:#1a2a4a; border:1px solid #4A90E2; color:#4A90E2; font-weight:bold;' : 'background:transparent; border:1px solid #555; color:#888;'}">
                                        972 🇮🇱
                                    </button>
                                    <input type="text" class="mgmt-input" data-field="whatsapp_prefix"
                                           style="width:60px; padding:3px 7px; font-size:0.82rem;
                                                  border-color:rgba(184,134,11,0.4); background:rgba(184,134,11,0.05); color:#d4a017;"
                                           value="${camp.whatsapp_prefix || ''}" placeholder="other">
                                    <span style="color:#888; font-size:0.8rem; font-family:monospace;">→ ${fullPhone || baseDigits}</span>
                                </div>` : '';
                return `${prefixField}
                                <a href="whatsapp://send?phone=${fullPhone || digits}&text=${encodeURIComponent(ContentManager.generateBilingualMessage(camp))}" class="wa-link">
                                    <span class="icon">💬</span> ${isIncomplete ? (fullPhone || digits) : raw}
                                </a>`;
            })()}
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
                        <label>Letter Code</label>
                        <select class="mgmt-input" data-field="ishmael_id" data-ishmael-select
                                onchange="ContentManager.syncIshmaelBadge('${campKey}', this.value)">
                            ${this.renderIshmaelOptions(camp)}
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
                    <button class="copy-btn" onclick="ContentManager.copyOnboardingMessage('${campKey}')">
                        Copy Message
                    </button>
                    <button onclick="ContentManager.toggleErase('${campKey}', this)"
                            style="margin-top: 8px; width: 100%; padding: 8px; border-radius: 6px; cursor: pointer;
                                   font-size: 0.8rem; transition: all 0.2s; letter-spacing: 0.5px;
                                   ${camp.marked_for_erasure
                ? 'background:rgba(220,38,38,0.15); border:1px solid #dc2626; color:#dc2626; font-weight:bold;'
                : 'background:transparent; border:1px solid #444; color:#555;'}">
                        ${camp.marked_for_erasure ? '🔴 Marked for Erasure' : '⌫ Mark for Erasure'}
                    </button>
                </div>
            </div>
        `;
    },

    resolveImagePath(path, bid) {
        if (!path || path.trim() === "") return '../assets/to_be_collected.png';
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

        console.log(`Filtering: Query="${query}", Status="${status}"`);

        cards.forEach(card => {
            const id = card.dataset.id;
            const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || (c.bids && c.bids[0])) === id);

            // If we can't find the campaign data, rely on card text for search, but status might be tricky
            const cardText = card.innerText.toLowerCase();
            const textMatch = !query || cardText.includes(query);

            let statusMatch = (status === 'all');
            if (camp) {
                statusMatch = statusMatch ||
                    (status === 'live' && (camp.status === 'live' || !!camp.whydonate_url)) ||
                    (status === 'redundant' && (camp.status === 'redundant' || camp.whatsapp === "972592640875")) ||
                    (status === 'verified' && camp.status === 'verified') ||
                    (status === 'pending' && camp.status === 'pending');
            } else {
                // Fallback for status if campaign data missing
                if (status === 'live') statusMatch = card.innerText.includes('LIVE ON WHYDONATE');
                if (status === 'redundant') statusMatch = card.innerText.includes('HUB OVERLAP');
            }

            if (textMatch && statusMatch) {
                card.style.display = 'grid';
            } else {
                card.style.display = 'none';
            }
        });
    },

    async updateLocalData(id, field, value) {
        const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || c.bids?.[0]) === id);
        if (camp) {
            camp[field] = value;
            console.log(`Updated ${id} field ${field} to:`, value);

            // Status → pending: always revoke letter assignment
            if (field === 'status' && value === 'pending') {
                camp.ishmael_id = null;
                const cardEl = document.querySelector(`.mgmt-card[data-id="${CSS.escape(id)}"]`);
                if (cardEl) {
                    const sel = cardEl.querySelector('[data-ishmael-select]');
                    if (sel) sel.value = '';
                    const tc = cardEl.querySelector('.token-container');
                    if (tc) tc.innerHTML = this.renderTitleTokens(camp, id);
                }
            }

            // Re-render only important parts if needed (skipping full render for titles to avoid button flickering)
            if (field === 'title' || field === 'identity_indices' || field === 'manual_identity') {
                const cardEl = document.querySelector(`.mgmt-card[data-id="${CSS.escape(id)}"]`);
                if (cardEl) {
                    const identitySpan = cardEl.querySelector('[data-identity-label]');
                    if (identitySpan) identitySpan.textContent = this.getDisplayName(camp);
                    const tc = cardEl.querySelector('.token-container');
                    if (tc) tc.innerHTML = this.renderTitleTokens(camp, id);
                }
            }
            if (field === 'ishmael_id') {
                this.render(); // Still need full render for letter code assignment changes as they affect multiple badges
            }

            await this.saveToServer();
            this.showSaveIndicator();
        }
    },

    openImageViewer(id) {
        const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || c.bids?.[0]) === id);
        if (!camp) return;

        // Collect all images: camp.images[] array OR single camp.image
        const images = Array.isArray(camp.images) && camp.images.length
            ? camp.images.map(img => this.resolveImagePath(img, id))
            : camp.image ? [this.resolveImagePath(camp.image, id)] : [];

        if (!images.length) return;

        let current = 0;
        const overlay = document.createElement('div');
        overlay.style.cssText = `position:fixed; inset:0; background:rgba(0,0,0,0.92); z-index:9999;
            display:flex; flex-direction:column; align-items:center; justify-content:center; gap:16px; cursor:pointer;`;

        const renderViewer = () => {
            overlay.innerHTML = `
                <div style="position:relative; max-width:90vw; max-height:80vh;">
                    <img src="${images[current]}" 
                         style="max-width:90vw; max-height:80vh; object-fit:contain; border-radius:8px; box-shadow:0 0 40px rgba(0,0,0,0.8);">
                    ${images.length > 1 ? `
                        <button onclick="event.stopPropagation(); ContentManager._viewerNav(-1)" 
                                style="position:absolute; left:-50px; top:50%; transform:translateY(-50%);
                                       background:rgba(255,255,255,0.1); border:none; color:#fff; font-size:2rem;
                                       padding:8px 14px; border-radius:6px; cursor:pointer;">‹</button>
                        <button onclick="event.stopPropagation(); ContentManager._viewerNav(1)" 
                                style="position:absolute; right:-50px; top:50%; transform:translateY(-50%);
                                       background:rgba(255,255,255,0.1); border:none; color:#fff; font-size:2rem;
                                       padding:8px 14px; border-radius:6px; cursor:pointer;">›</button>` : ''}
                </div>
                ${images.length > 1 ? `
                    <div style="display:flex; gap:8px;">
                        ${images.map((src, i) => `
                            <img src="${src}" onclick="event.stopPropagation(); ContentManager._viewerNav(${i - current})"
                                 style="width:60px; height:60px; object-fit:cover; border-radius:4px; cursor:pointer;
                                        opacity:${i === current ? 1 : 0.4}; border:2px solid ${i === current ? '#d4a017' : 'transparent'}; transition:all 0.2s;">
                        `).join('')}
                    </div>` : ''}
                <div style="color:#888; font-size:0.8rem;">${images.length > 1 ? `${current + 1} / ${images.length} — ` : ''}Click anywhere to close · Esc</div>`;
        };

        this._viewerNav = (delta) => {
            current = (current + delta + images.length) % images.length;
            renderViewer();
        };

        overlay.addEventListener('click', () => overlay.remove());
        const onKey = (e) => {
            if (e.key === 'Escape') { overlay.remove(); document.removeEventListener('keydown', onKey); }
            else if (e.key === 'ArrowRight') this._viewerNav(1);
            else if (e.key === 'ArrowLeft') this._viewerNav(-1);
        };
        document.addEventListener('keydown', onKey);

        renderViewer();
        document.body.appendChild(overlay);
    },

    async translateField(id, field, btn) {
        const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || c.bids?.[0]) === id);
        if (!camp) return;

        const arabicText = camp[field] || '';
        if (!arabicText.trim()) return;

        const orig = btn.textContent;
        btn.textContent = '⏳ Translating…';
        btn.disabled = true;

        try {
            const apiBase = window.location.port === '4040' ? 'http://127.0.0.1:5010' : '';
            const resp = await fetch(`${apiBase}/api/translate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: arabicText, mode: field })
            });
            const data = await resp.json();
            if (data.error) throw new Error(data.error);

            const bilingual = data.bilingual || `${data.translation} | ${arabicText}`;

            // Critical: Update local data and trigger save
            await this.updateLocalData(id, field, bilingual);

            // Update UI elements manually for immediate feedback
            const cardEl = document.querySelector(`.mgmt-card[data-id="${CSS.escape(id)}"]`);
            if (cardEl) {
                if (field === 'title') {
                    const inp = cardEl.querySelector('.title-editor');
                    if (inp) {
                        inp.value = bilingual;
                        this.handleTitleInput(inp);
                    }
                    const tc = cardEl.querySelector('.token-container');
                    if (tc) tc.innerHTML = this.renderTitleTokens(camp, id);
                } else {
                    const ta = cardEl.querySelector('.description-editor');
                    if (ta) ta.value = bilingual;
                }
            }
            btn.textContent = '✅ Done';
            setTimeout(() => {
                btn.textContent = orig;
                btn.disabled = false;
                // Only re-render if it was a title (to update identity)
                if (field === 'title') this.render();
            }, 1000);
        } catch (err) {
            console.error('Translation error:', err);
            btn.textContent = '❌ Fail (Check API Key)';
            setTimeout(() => { btn.textContent = orig; btn.disabled = false; }, 3000);
        }
    },

    toggleErase(id, btn) {
        const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || c.bids?.[0]) === id);
        if (!camp) return;
        camp.marked_for_erasure = !camp.marked_for_erasure;

        // Update button
        btn.textContent = camp.marked_for_erasure ? '🔴 Marked for Erasure' : '⌫ Mark for Erasure';
        Object.assign(btn.style, camp.marked_for_erasure
            ? { background: 'rgba(220,38,38,0.15)', borderColor: '#dc2626', color: '#dc2626', fontWeight: 'bold' }
            : { background: 'transparent', borderColor: '#444', color: '#666', fontWeight: 'normal' });

        // Dim card
        const cardEl = document.querySelector(`.mgmt-card[data-id="${id}"]`);
        if (cardEl) {
            const img = cardEl.querySelector('.mgmt-img');
            if (img) { img.style.opacity = camp.marked_for_erasure ? '0.35' : ''; img.style.filter = camp.marked_for_erasure ? 'grayscale(1)' : ''; }
            cardEl.style.borderColor = camp.marked_for_erasure ? '#dc2626' : '';
            cardEl.style.opacity = camp.marked_for_erasure ? '0.7' : '';
        }

        this.saveToServer();
        this.showSaveIndicator();
    },

    setPrefix(id, prefix, btn) {
        const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || c.bids?.[0]) === id);
        if (!camp) return;
        // Toggle off if already selected
        camp.whatsapp_prefix = (camp.whatsapp_prefix === prefix) ? '' : prefix;
        // Re-render this card's contact section by doing a full card re-render
        // (contact section is too embedded for surgical patch)
        const cardEl = document.querySelector(`.mgmt-card[data-id="${id}"]`);
        if (cardEl) {
            const newCard = document.createElement('div');
            newCard.innerHTML = this.createCard(camp);
            cardEl.replaceWith(newCard.firstElementChild);
        }
        this.saveToServer();
        this.showSaveIndicator();
    },

    copyField(bid, field, btn) {
        const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || c.bids?.[0]) === bid);
        if (!camp) return;

        let text = "";
        const identity = this.getDisplayName(camp);
        const beneficiaryLine = `Beneficiary: ${identity}, Gaza`;

        if (field === 'identity') text = beneficiaryLine;
        else if (field === 'title') text = camp.title;
        else if (field === 'description') text = `${beneficiaryLine}\n\n${camp.description}`;
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
            // Stamp the computed identity_name onto each campaign so the server
            // has the correct reconstructed name (from title tokens) for message generation
            const enriched = this.campaigns.map(c => ({
                ...c,
                identity_name: this.getDisplayName(c)
            }));
            const response = await fetch('/api/growth-list-save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(enriched)
            });
            if (!response.ok) throw new Error('Save failed');
        } catch (error) {
            console.error('Error saving to server:', error);
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

    async copyOnboardingMessage(id) {
        const camp = this.campaigns.find(c => (c.norm_whatsapp || c.bid || c.bids?.[0]) === id);
        if (!camp) return;

        const btn = document.querySelector(`[data-id="${CSS.escape(id)}"] .copy-btn`);
        if (btn) { btn.innerText = '⏳ Saving...'; btn.disabled = true; }

        try {
            // Step 1: Save the current live page data to server.
            // This triggers _regenerate_onboarding_messages on the server side
            // with the correct whatsapp_prefix, whydonate_url, etc.
            await this.saveToServer();

            // Step 2: Small pause for regeneration to complete
            await new Promise(r => setTimeout(r, 400));

            // Step 3: Fetch the freshly regenerated message.
            // Use the raw whatsapp digits for lookup (server normalizes by stripping + and viral_)
            const lookupId = (camp.whatsapp || camp.norm_whatsapp || camp.bid || camp.bids?.[0] || id)
                .toString().replace(/\D/g, '');
            const resp = await fetch(`/api/onboarding-message/${encodeURIComponent(lookupId)}?v=${Date.now()}`);
            const message = resp.ok ? await resp.text() : this.generateBilingualMessage(camp);

            await navigator.clipboard.writeText(message);

            if (btn) {
                btn.innerText = '✅ Copied!';
                btn.classList.add('success');
                btn.disabled = false;
                setTimeout(() => { btn.innerText = '📋 Copy Message'; btn.classList.remove('success'); }, 2500);
            }
        } catch (err) {
            console.error('Copy failed:', err);
            if (btn) { btn.innerText = '📋 Copy Message'; btn.disabled = false; }
            navigator.clipboard.writeText(this.generateBilingualMessage(camp));
        }
    },

    // --- SUBMISSIONS FETCH & ASSETS ---
    submissionsCache: {},

    async toggleSubmissions(id, btn) {
        const panel = document.getElementById(`subs-${id}`);
        if (!panel) return;

        if (panel.style.display === 'block' && !btn) {
            panel.style.display = 'none';
            return;
        }

        if (panel.style.display === 'block' && btn) {
            panel.style.display = 'none';
            btn.innerText = '🔍 Fetch Submissions';
            return;
        }

        panel.style.display = 'block';
        if (btn) {
            btn.innerText = '⏳ Loading...';
            btn.classList.add('loading');
        }

        try {
            const data = await this.fetchSubmissions(id);
            this.submissionsCache[id] = data;
            this.renderSubmissions(id, data);
        } catch (err) {
            console.error('Fetch failed:', err);
            panel.querySelector('.subs-content').innerHTML = `<p style="color: #FF4B2B; font-size: 0.8rem; padding:10px;">Error connecting to submission archive.</p>`;
        } finally {
            if (btn) {
                btn.innerText = '🔍 Refresh Assets';
                btn.classList.remove('loading');
            }
        }
    },

    async fetchSubmissions(id) {
        // Extract digits for lookup
        const lookupId = id.toString().replace(/\D/g, '');
        const resp = await fetch(`/api/submissions/${encodeURIComponent(lookupId)}?v=${Date.now()}`);
        if (!resp.ok) throw new Error('API failed');
        return await resp.json();
    },

    renderSubmissions(id, data) {
        const panel = document.getElementById(`subs-${id}`);
        const container = panel.querySelector('.subs-content');
        if (!data || data.length === 0) {
            container.innerHTML = `<p style="color: #666; font-size: 0.8rem; font-style: italic; padding:10px;">No recent submissions found for this ID.</p>`;
            return;
        }

        let html = '';
        data.forEach((sub, idx) => {
            const dateStr = sub.timestamp ? new Date(sub.timestamp).toLocaleDateString() : 'New Lead';

            // Text Assets
            if (sub.title || sub.story) {
                html += `
                    <div class="asset-text-item" onclick="ContentManager.copySubmissionText('${id}', ${idx}, this)">
                        <small>${dateStr} | Source: ${sub.source || 'Web'}</small>
                        <div style="font-weight: bold; margin-bottom: 2px; color: var(--color-primary);">${sub.title || '(Untitled)'}</div>
                        <div class="story-preview" style="font-size: 0.75rem; color: #8b949e; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">
                            ${sub.story || '(No story text)'}
                        </div>
                    </div>
                `;
            }

            // Image Grid
            if ((sub.images && sub.images.length > 0) || (sub.image_urls && sub.image_urls.length > 0)) {
                html += `<div class="asset-grid">`;
                const imgList = (sub.image_urls && sub.image_urls.length > 0) ? sub.image_urls : sub.images;

                imgList.forEach((url, imgIdx) => {
                    const displayUrl = url.startsWith('data:') ? url : url;
                    const localPath = sub.local_paths ? sub.local_paths[imgIdx] : '';

                    html += `
                        <div class="asset-item-wrapper" style="position:relative; display:inline-block;">
                            <div class="asset-item" onclick="ContentManager.copySubmissionImage('${url}', this)">
                                <img src="${displayUrl}" alt="Asset">
                                <div class="overlay">CLICK TO COPY</div>
                            </div>
                            ${localPath ? `
                                <button class="btn-copy-path" 
                                    data-path="${localPath}"
                                    onclick="event.stopPropagation(); ContentManager.copyToClipboardFromBtn(this)"
                                    title="${localPath}"
                                    style="position:absolute; bottom:5px; right:5px; padding:2px 5px; font-size:9px; background: rgba(0,0,0,0.7); color:#fff; border:1px solid rgba(255,255,255,0.3); border-radius:3px; cursor:pointer; z-index:10; font-family:monospace; opacity:0.8;">
                                    Copy Path
                                </button>
                            ` : ''}
                        </div>
                    `;
                });
                html += `</div>`;
            }
        });

        container.innerHTML = html;
    },

    async copySubmissionText(id, index, el) {
        const sub = this.submissionsCache[id]?.[index];
        if (!sub) return;

        const text = `${sub.title || ''}\n\n${sub.story || ''}`.trim();
        await navigator.clipboard.writeText(text);

        const originalHTML = el.innerHTML;
        el.style.borderColor = '#32BF55';
        el.innerHTML = '<div style="color:#32BF55; font-weight:bold; text-align:center; padding:10px;">✓ COPIED TEXT</div>';
        setTimeout(() => {
            el.style.borderColor = '';
            el.innerHTML = originalHTML;
        }, 1500);
    },

    async copySubmissionImage(url, el) {
        const overlay = el.querySelector('.overlay');
        const originalText = overlay.innerText;
        overlay.innerText = '⏳ PROCESSING...';
        overlay.style.opacity = '1';

        try {
            const resp = await fetch(url);
            const blob = await resp.blob();

            // Use canvas to ensure it's a PNG for clipboard
            const img = new Image();
            img.src = URL.createObjectURL(blob);
            await new Promise(r => img.onload = r);

            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            canvas.getContext('2d').drawImage(img, 0, 0);

            canvas.toBlob(async (pngBlob) => {
                const item = new ClipboardItem({ 'image/png': pngBlob });
                await navigator.clipboard.write([item]);
                overlay.innerText = '✅ COPIED IMAGE';
                overlay.style.background = 'rgba(50, 191, 85, 0.8)';
                setTimeout(() => {
                    overlay.innerText = originalText;
                    overlay.style.background = '';
                    overlay.style.opacity = '';
                }, 2000);
            }, 'image/png');
        } catch (err) {
            console.error('Image copy failed:', err);
            overlay.innerText = '❌ FAILED';
            setTimeout(() => {
                overlay.innerText = originalText;
                overlay.style.opacity = '';
            }, 2000);
        }
    },
    async copyToClipboardFromBtn(btn) {
        const text = btn.getAttribute('data-path');
        if (!text) return;
        try {
            await navigator.clipboard.writeText(text);
            const originalText = btn.innerText;
            btn.innerText = '✓ Copied';
            btn.style.background = '#32BF55';
            setTimeout(() => {
                btn.innerText = originalText;
                btn.style.background = '';
            }, 2000);
        } catch (err) {
            console.error('Copy failed:', err);
            // Fallback for non-secure contexts or permission issues
            const el = document.createElement('textarea');
            el.value = text;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            btn.innerText = '✓ Copied';
            setTimeout(() => { btn.innerText = 'Copy Path'; }, 2000);
        }
    },

    generateBilingualMessage(camp) {
        const beneficiaryID = camp.norm_whatsapp || camp.bid || camp.bids?.[0] || 'unknown';
        const identity = this.getDisplayName(camp);
        const whydonateLink = camp.whydonate_url || '[PENDING LINK]';

        if (this.onboardingTemplate) {
            console.log(`✅ Generating full message for ${identity} using template...`);
            let msg = this.onboardingTemplate;
            const PAGES_ROOT = "https://dours-d.github.io/local-ai-campaign-assistant";

            msg = msg.replace(/\[BENEFICIARY_ID\]/g, beneficiaryID);
            msg = msg.replace(/\[BENEFICIARY_NAME\]/g, identity);
            msg = msg.replace(/\[WHYDONATE_LINK\]/g, whydonateLink);
            msg = msg.replace(/\[COLLECTIVE_SHIELD_LINK\]/g, PAGES_ROOT + "/");
            msg = msg.replace(/\[AI_DUNYA_LINK\]/g, PAGES_ROOT + "/brain.html");
            msg = msg.replace(/\[CORRECTION_PORTAL_LINK\]/g, PAGES_ROOT + "/index.html#/onboard/" + beneficiaryID);
            // Also replace any stale fajr.today references in the template body
            msg = msg.replace(/https:\/\/fajr\.today\//g, PAGES_ROOT + "/");
            msg = msg.replace(/https:\/\/fajr\.today/g, PAGES_ROOT);

            return msg;
        }

        console.warn('⚠️ Template not found (this.onboardingTemplate is empty), falling back to legacy short message.');

        // Fallback to legacy short message if template fetch failed
        const ishmaelIDs = this.getIshmaelIDs();
        const activeTrustee = ishmaelIDs.find(i => i.id === camp.ishmael_id);
        const shortID = activeTrustee ? `${activeTrustee.id}#${activeTrustee.num}` : 'Pending';

        return `Salam, ${identity} (ID: ${shortID})\n\nThis is your onboarding link: ${whydonateLink}\n\n---\n\nسلام ، ${identity} (ID: ${shortID})\n\nهذا هو رابط الانضمام الخاص بك: ${whydonateLink}`;
    },

    async copyFajrImage(btn) {
        try {
            const response = await fetch('images/fajr.jpg');
            const blob = await response.blob();

            // Clipboard API usually requires PNG for images
            // We'll use a canvas to convert if needed, but first try raw blob if it's supported
            // Actually, for best compatibility, PNG is safer.
            const img = new Image();
            img.src = URL.createObjectURL(blob);
            await new Promise(resolve => img.onload = resolve);

            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);

            canvas.toBlob(async (pngBlob) => {
                try {
                    const item = new ClipboardItem({ 'image/png': pngBlob });
                    await navigator.clipboard.write([item]);

                    const originalText = btn.innerText;
                    btn.innerText = '✅ COPIED!';
                    btn.style.background = '#32BF55';
                    setTimeout(() => {
                        btn.innerText = originalText;
                        btn.style.background = '';
                    }, 2000);
                } catch (err) {
                    console.error('Clipboard write failed:', err);
                    alert('Clipboard access denied or unsupported.');
                }
            }, 'image/png');

        } catch (error) {
            console.error('Error copying Fajr image:', error);
            alert('Failed to copy image.');
        }
    }
};

// Expose to window for inline onclick handlers
window.ContentManager = ContentManager;

document.addEventListener('DOMContentLoaded', () => ContentManager.init());
