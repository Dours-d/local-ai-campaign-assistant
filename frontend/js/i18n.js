/**
 * Language Toggle System
 * Supports Arabic (ar) and English (en)
 * Stores preference in localStorage
 */

const i18n = {
    currentLang: localStorage.getItem('lang') || 'en',

    translations: {
        en: {
            // Navigation
            nav_mission: 'Amanah',
            nav_impact: 'Shahada',
            nav_campaigns: 'The Field',
            nav_contact: 'Direct Line',
            nav_donate: 'Bear Witness',

            // Hero
            hero_title: 'End of the [night]<br>Rise of the [Sovereign]',
            hero_subtitle: 'Fajr is the clarity found at the threshold of the dawn. We do not "distribute aid"—we fulfill a collective Amanah. Rooted in the resilience of the olive tree, we reclaim our autonomy and support our people directly.',
            hero_cta: 'FULFILL THE AMANAH',
            hero_secondary: 'Our Logic',

            // Impact section (Shahada)
            impact_title: 'The Weight of Our Shahada',
            impact_communities: 'Nodes of Autonomy',
            impact_projects: 'Direct Interventions',
            impact_lives: 'Sovereign Lives',
            impact_transparency: '% Direct Flow',

            // About section
            about_title: 'Fulfillment in Action',
            about_text: 'Fajr.today is a sovereign bridge, not an NGO. We bypass the "Rockefeller" programming of global aid to ensure that resources reach the destination without being lost to corporate friction. Our €100 batching logic is a technical proof of our honesty, moving money only when it preserves its value.',
            about_cta: 'The Ledger Logic',

            // Campaigns section
            campaigns_title: 'Solidarity Tracks',
            campaign_monthly_title: 'Constant Flow',
            campaign_monthly_desc: 'Provide steady, reliable energy to our nodes through self-custodied monthly commitments.',
            campaign_monthly_cta: 'COMMIT MONTHLY',
            campaign_once_title: 'Single Strike',
            campaign_once_desc: 'Immediate injection of resources for tactical, high-priority humanitarian needs.',
            campaign_once_cta: 'STRIKE ONCE',
            campaign_resilience_title: 'Sovereign Fund',
            campaign_resilience_desc: 'Long-term community reconstruction and infrastructure for a life after the siege.',
            campaign_resilience_cta: 'VIEW THE FIELD',

            // Footer
            footer_rights: '© 2026 Sovereign Fajr Network. No programming accepted.',

            // Toggle
            lang_toggle: 'عربي'
        },
        ar: {
            // Navigation
            nav_mission: 'الأمانة',
            nav_impact: 'الشهادة',
            nav_campaigns: 'الميدان',
            nav_contact: 'الخط المباشر',
            nav_donate: 'كن شاهداً',

            // Hero
            hero_title: 'نهاية الليل<br>وصعود السيادة',
            hero_subtitle: 'الفجر هو الوضوح الموجود عند عتبة الفجر. نحن لا نوزع مساعدات، بل نؤدي أمانة جماعية. متجذرون في صمود شجرة الزيتون، نستعيد استقلاليتنا وندعم أهلنا مباشرة.',
            hero_cta: 'أدِّ الأمانة الآن',
            hero_secondary: 'منطقنا',

            // Impact section (Shahada)
            impact_title: 'ثقل شهادتنا',
            impact_communities: 'عقد الحكم الذاتي',
            impact_projects: 'تدخلات مباشرة',
            impact_lives: 'أنفس حرة',
            impact_transparency: '% تدفق مباشر',

            // About section
            about_title: 'التنفيذ في العمل',
            about_text: 'فجر.اليوم هو جسر سيادي، وليس منظمة غير حكومية. نحن نتجاوز "برمجيات روكفلر" للمساعدات العالمية لضمان وصول الموارد إلى وجهتها دون ضياع في الاحتكاك المؤسسي. منطق التجميع لمبلغ ١٠٠ يورو هو دليل تقني على صدقنا، حيث ننقل الأموال فقط عندما تحافظ على قيمتها.',
            about_cta: 'منطق السجل',

            // Campaigns section
            campaigns_title: 'مسارات التضامن',
            campaign_monthly_title: 'تدفق ثابت',
            campaign_monthly_desc: 'قدم طاقة ثابتة وموثوقة لعقدنا من خلال التزامات شهرية ذاتية.',
            campaign_monthly_cta: 'التزم شهرياً',
            campaign_once_title: 'ضربة واحدة',
            campaign_once_desc: 'حقن فوري للموارد للاحتياجات الإنسانية التكتيكية ذات الأولوية العالية.',
            campaign_once_cta: 'تبرع فوراً',
            campaign_resilience_title: 'الصندوق السيادي',
            campaign_resilience_desc: 'إعادة بناء المجتمع على المدى الطويل وبناء البنية التحتية لحياة ما بعد الحصار.',
            campaign_resilience_cta: 'عرض الميدان',

            // Footer
            footer_rights: '© ٢٠٢٦ شبكة فجر السيادية. لا نقبل البرمجة الخارجية.',

            // Toggle
            lang_toggle: 'English'
        }
    },

    t(key) {
        return this.translations[this.currentLang][key] || key;
    },

    setLang(lang) {
        this.currentLang = lang;
        localStorage.setItem('lang', lang);
        document.documentElement.lang = lang;
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
        this.updatePage();
    },

    toggle() {
        this.setLang(this.currentLang === 'en' ? 'ar' : 'en');
    },

    updatePage() {
        // Update all elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            el.innerHTML = this.t(key);
        });

        // Update toggle button text
        const toggleBtn = document.getElementById('lang-toggle');
        if (toggleBtn) {
            toggleBtn.textContent = this.t('lang_toggle');
        }
    },

    init() {
        document.documentElement.lang = this.currentLang;
        document.documentElement.dir = this.currentLang === 'ar' ? 'rtl' : 'ltr';
        this.updatePage();
    }
};

// Initialize on DOM load
window.addEventListener('DOMContentLoaded', () => {
    i18n.init();
});
