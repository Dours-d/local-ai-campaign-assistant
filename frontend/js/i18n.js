/**
 * Language Toggle System
 * Supports Arabic (ar) and English (en)
 * Stores preference in localStorage
 */

const i18n = {
    currentLang: 'ar', // Forced Arabic-First direction

    translations: {
        en: {
            // Navigation
            nav_mission: 'Amanah',
            nav_impact: 'Shahada',
            nav_campaigns: 'The Field',
            nav_contact: 'Direct Line',
            nav_donate: 'Bear Witness',

            // Hero
            hero_title: 'End of the [Night]<br>Begeting [Resilience]',
            hero_subtitle: 'The night is over. The Sovereign rise. No programming. No gatekeepers. Just the direct witness of the field.',
            hero_cta: 'FULFILL THE AMANAH',
            hero_secondary: 'The Logic',

            // Impact section
            impact_title: 'Evidence of Truth',
            impact_communities: 'Days of Witness',
            impact_projects: 'Proofs of Truth',
            impact_lives: 'EUR Batch Honesty',
            impact_transparency: 'Corporate Friction (Chuffed)',

            // About section
            about_title: 'Trust in Action',
            about_text: 'Fajr.today is a sovereign bridge, not an NGO. We bypass the "Rockefeller" programming of global aid to ensure that resources reach the destination without being lost to corporate friction.',
            about_cta: 'The Ledger Logic',

            // Footer
            footer_rights: '© 2026 · fajr.today',

            // Campaigns section
            campaigns_title: 'Paths of the Amanah',
            campaign_monthly_title: 'Sustained Autonomy',
            campaign_monthly_desc: 'Provide predictable support to ensure the independence of the field.',
            campaign_monthly_cta: 'SUSTAIN',
            campaign_once_title: 'Direct Strike',
            campaign_once_desc: 'Immediate intervention for the most urgent field requirements.',
            campaign_once_cta: 'STRIKE NOW',
            campaign_resilience_title: 'Sovereign Fund',
            campaign_resilience_desc: 'Building autonomous infrastructure to bypass all external programming.',
            campaign_resilience_cta: 'BECOME SOVEREIGN'
        },
        ar: {
            // Navigation
            nav_mission: 'الأمانة',
            nav_impact: 'الشهادة',
            nav_campaigns: 'الميدان',
            nav_contact: 'الخط المباشر',
            nav_donate: 'كن شاهداً',

            // Hero
            hero_title: 'انقضاء [الليل]<br>بزوغ [الفجر]',
            hero_subtitle: 'انتهى الليل. نهوض السيادة. لا برمجة. لا وسطاء. فقط الحقيقة المباشرة للأمانة في الميدان.',
            hero_cta: 'أدِّ الأمانة الآن',
            hero_secondary: 'منطقنا',

            // Impact section
            impact_title: 'بينة الحق',
            impact_communities: 'أيام الشهادة المباشرة',
            impact_projects: 'براهين مسجلة للحق',
            impact_lives: 'صدق تجميع (١٠٠) يورو',
            impact_transparency: 'احتكاك الشركات (Chuffed)',

            // About section
            about_title: 'التنفيذ في العمل',
            about_text: 'فجر.اليوم هو جسر سيادي، وليس منظمة غير حكومية. نحن نتجاوز "برمجيات روكفلر" للمساعدات العالمية لضمان وصول الموارد إلى وجهتها.',
            about_cta: 'منطق السجل',

            // Footer
            footer_rights: '© ٢٠٢٦ · fajr.today',

            // Campaigns section
            campaigns_title: 'مسارات الأمانة',
            campaign_monthly_title: 'استدامة الحكم الذاتي',
            campaign_monthly_desc: 'توفير دعم يمكن التنبؤ به لضمان استقلال الميدان.',
            campaign_monthly_cta: 'استدامة الأمانة',
            campaign_once_title: 'ضربة مباشرة',
            campaign_once_desc: 'تدخل فوري لأكثر متطلبات الميدان إلحاحاً.',
            campaign_once_cta: 'اضرب الآن',
            campaign_resilience_title: 'صندوق السيادة',
            campaign_resilience_desc: 'بناء بنية تحتية مستقلة لتجاوز كافة البرمجيات الخارجية.',
            campaign_resilience_cta: 'كن سيادياً'
        }
    },

    t(key, lang) {
        return this.translations[lang][key] || key;
    },

    // Toggle removed as per Pixel-Perfect bilingual spec
    setLang(lang) {
        // No-op to prevent breakage
    },

    toggle() {
        // No-op to prevent breakage
    },

    updatePage() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            const arText = this.t(key, 'ar');
            const enText = this.t(key, 'en');

            // Specialized injection for the Hero title to maintain colossal scale
            if (key === 'hero_title') {
                el.innerHTML = `
                    <div class="lang-dual hero-title-bundle">
                        <span class="ar-main">${arText}</span>
                        <span class="en-sub">${enText}</span>
                    </div>
                `;
            } else {
                el.innerHTML = `
                    <div class="lang-dual">
                        <span class="ar-main">${arText}</span>
                        <span class="en-sub">${enText}</span>
                    </div>
                `;
            }
        });
    },

    init() {
        document.documentElement.lang = 'ar';
        document.documentElement.dir = 'rtl';
        this.updatePage();
    }
};

// Initialize on DOM load
window.addEventListener('DOMContentLoaded', () => {
    i18n.init();
});
