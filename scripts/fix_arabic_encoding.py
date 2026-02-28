import re

def fix_index_html():
    path = "onboarding/index.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # The dictionary replacement
    ar_dict_good = """            ar: {
                page_title: "بوابة غزة للصمود",
                header_title: "صندوق غزة العالمي للصمود",
                header_subtitle: "بوابة توثيق المساعدات والشفافية الموحدة",
                welcome_title: "السلام عليكم ورحمة الله",
                updating_profile: "تحديث ملف:",
                not_you: "ليس أنت؟ ابدأ من جديد",
                welcome_desc: "لدعمكم بشكل فعال، نتبع عملية شفافة تماماً مصممة لضمان سيادتكم الرقمية.",
                li_transparency: "شفافية 100% من خلال معرفات شخصية فريدة.",
                li_wallet_label: "محفظة رقمية:",
                li_wallet_text: "يتم تخصيص عنوان آمن فريد لملفك لتجميع المساعدات.",
                li_trust_label: "إدارة الأمانة:",
                li_trust_text: "يمكننا إدارة محفظتك أثناء تعلمك المبادئ الأولى للعملات المشفرة، لضمان الأمن والسيادة.",
                li_threshold_label: "حد الاستدامة:",
                li_threshold_text: "100 يورو كحد أدنى لضمان تحويلات فعالة وذات مغزى.",
                li_sustainability_label: "استمرارية النظام (25%)",
                li_sustainability_text: "لصيانة النظام والأتمتة.",
                li_audits: "تقارير تدقيق شاملة للنظام كل يوم اثنين.",
                btn_agree: "موافق والمتابعة",
                step2_title: "تفاصيل الحملة",
                label_title: "العنوان المقترح (اختياري)",
                placeholder_title: "مثال: ساعدوا عائلتي في إعادة البناء...",
                label_story: "قصتك (اختياري)",
                placeholder_story: "أخبرنا بما حدث وما تحتاجه...",
                label_media: "تحميل الوسائط (صور/فيديو)",
                media_help: "اختر صوراً أو فيديوهات متعددة تروي قصتك.",
                btn_back: "رجوع",
                btn_next: "التالي",
                step3_title: "المراجعة النهائية",
                step3_desc: "سيتم تخصيص رقم تعريفي فريد لك عند مزامنة المستندات.",
                label_whatsapp: "واتساب",
                placeholder_whatsapp: "+970 ...",
                whatsapp_help: "يمكنك تزويدنا برقم إذا كنت ترغب في التواصل معك (اختياري تماماً).",
                error_invalid_phone: "ملاحظة: تبدأ أرقام الهاتف عادة بـ +.",
                label_name: "الاسم المفضل",
                placeholder_name: "الاسم الأول فقط",
                label_wallet: "محفظتك الرقمية (اختياري)",
                placeholder_wallet: "عنوان USDT (TRC20)",
                wallet_help: "إذا كانت لديك محفظتك الخاصة TRC20، يمكنك تزويدنا بها هنا.",
                agree_policy: "بإرسالك لهذا الطلب، فإنك توافق على سياسات الشفافية وعدم الهدر.",
                btn_submit: "إرسال",
                btn_uploading: "جاري الإرسال...",
                success_title: "نجاح!",
                success_desc: "تم استلام تفاصيلك وتحديثاتك. سيتم مزامنة مسودة صندوق غزة العالمي للصمود مع آخر تغييراتك تلقائياً.",
                success_footer: "راجع منسقك يوم الاثنين للحصول على تقرير التدقيق.",
                lookup_desc: "أدخل رقم الواتساب الخاص بك للوصول إلى حملتك:",
                btn_go: "دخول",
                lookup_help: "التنسيق: رمز الدولة + الرقم (بدون + أو مسافات)",
                out_of_scope: "هذا الرقم غير مسجل في نطاق مساعداتنا الحالي. يرجى التواصل مع المنسق الخاص بك.",
                access_noor: "استكشف ذاكرتنا الجماعية:",
                btn_noor: "الدخول إلى بوابة نور المعرفية"
            }"""
    
    # regex replace the ar: { ... } block
    content = re.sub(r'ar:\s*\{.*?\n\s*\}', ar_dict_good, content, flags=re.DOTALL)
    
    # replace inline alerts
    content = re.sub(r'alert\(currentLang === \'ar\' \? ".*?" : "Please enter a valid phone number with country code."\);', 
                     'alert(currentLang === \'ar\' ? "يرجى إدخال رقم هاتف صحيح مع رمز الدولة." : "Please enter a valid phone number with country code.");', content)
                     
    content = re.sub(r'const errorMsg = currentLang === \'ar\' \? `.*?\(Error \$\{status\}\).*?` : `Submission failed \(Error \$\{status\}\)\. Please try again\.`;',
                     'const errorMsg = currentLang === \'ar\' ? `فشل الإرسال (Error ${status}). يرجى المحاولة مرة أخرى.` : `Submission failed (Error ${status}). Please try again.`;', content)
                     
    content = re.sub(r'const errorMsg = currentLang === \'ar\' \? \'.*?\' \: \'Connection error\. Please try again\.\';',
                     'const errorMsg = currentLang === \'ar\' ? \'حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.\' : \'Connection error. Please try again.\';', content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def fix_brain_html():
    path = "onboarding/brain.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # The dictionary replacement
    ar_dict_good = """            ar: {
                back_to_portal: "العودة إلى بوابة التمكين",
                ki_title: "عناصر المعرفة",
                discovering: "جاري اكتشاف البيانات...",
                brain_dark: "الذاكرة حالياً في وضع السكون.",
                conn_lost: "انقطع الاتصال بالشبكة الجماعية.",
                retrieving: "جاري استرجاع البيانات المقطرة...",
                failed_item: "فشل تحميل هذا العنصر.",
                noor_intro: "أنا نور. كيف يمكنني مساعدة المهمة اليوم؟",
                processing: "جاري المعالجة...",
                unavailable: "محول الذكاء غير متاح حالياً. يرجى التأكد من أن النموذج المحلي نشط.",
                conn_error: "خطأ في الاتصال بالذاكرة المحلية.",
                online: "متصل",
                offline_mode: "غير متصل (وضع الأرشيف)",
                enter_key: "أدخل مفتاح الدخول السيادي لإنشاء اتصال آمن.",
                authenticate: "توثيق",
                relay: "مرحل",
                ask_noor: "اسأل نور...",
                send: "إرسال"
            }"""
    
    content = re.sub(r'ar:\s*\{.*?\n\s*\}', ar_dict_good, content, flags=re.DOTALL)
    
    # Replace other specific elements safely using specific known prefixes
    
    # DUNYA Header in login
    content = re.sub(r'DUNYA Ø¯Ù\†ÙŠØ§', 'DUNYA دنيا', content)
    
    # Return to portal
    content = re.sub(r'â†  <span data-i18n="back_to_portal">Return to Sovereign Portal</span></a>\s*<header>\s*<h1>DUNYA Ø¯Ù\†ÙŠØ§</h1>', 
                     '← <span data-i18n="back_to_portal">Return to Sovereign Portal</span></a>\n        <header>\n            <h1>DUNYA دنيا</h1>', content)
    
    # Doléances Title
    content = re.sub(r'ðŸ“£ DolÃ©ances â€” Ø´ÙƒØ§ÙˆÙ‰ Ø§Ù„Ø£Ù…Ø§Ù†Ø©', '📢 Doléances — شكاوى الأمانة', content)
    
    # Doléances text
    content = re.sub(r'<span dir="rtl" style="display:block; margin-top:6px;">.*?</span>', 
                     '<span dir="rtl" style="display:block; margin-top:6px;">قدّم شكوى أو قلقاً حول الأمانة. الهوية اختيارية — يمكنك البقاء مجهولاً. إذا أضفت رقم هاتف أو معرّف أو رابط حملة، ستكون شكواك قابلة للتتبع والمعالجة.</span>', content, flags=re.DOTALL)
                     
    # Complaint success
    content = re.sub(r'âœ“ Your complaint has been recorded\. .*?</div>', 
                     '✓ Your complaint has been recorded. جرى تسجيل شكواك.\n            </div>', content)
                     
    # Textarea placeholder
    content = re.sub(r'placeholder="Describe your complaint or concern about the Trust\.\.\. / .*?"',
                     'placeholder="Describe your complaint or concern about the Trust... / اكتب شكواك أو قلقك هنا..."', content)
                     
    # Submit anonymously
    content = re.sub(r'Submit anonymously / .*?\s*</label>',
                     'Submit anonymously / تقديم مجهول\n                    </label>', content)
                     
    # Identifier placeholder
    content = re.sub(r'placeholder="Phone number, beneficiary ID, or campaign link \(optional\) / .*?"',
                     'placeholder="Phone number, beneficiary ID, or campaign link (optional) / رقم الهاتف أو المعرّف أو رابط الحملة"', content)
                     
    # Submit button
    content = re.sub(r'ðŸ“¤ Submit Complaint â€” .*?\n\s*</button>',
                     '📤 Submit Complaint — إرسال الشكوى\n                </button>', content)

    # Emoji in login card
    content = re.sub(r'ðŸŒ ', '🌐', content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

fix_index_html()
fix_brain_html()
print("Encoding applied successfully.")
