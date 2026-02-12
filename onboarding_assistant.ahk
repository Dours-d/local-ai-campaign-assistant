; Onboarding Assistant - AutoHotkey Script
; Hotkey: Ctrl+Alt+O
; Copies selected text, generates onboarding message, and copies to clipboard

#SingleInstance Force
SetTitleMatchMode, 2

; Configuration
PORTAL_URL := "https://dours-d.github.io/local-ai-campaign-assistant/onboard.html"

; Hotkey: Ctrl+Alt+O
^!o::
{
    ; Save original clipboard
    ClipSaved := ClipboardAll
    Clipboard := ""
    
    ; Copy selected text
    Send, ^c
    ClipWait, 1
    
    if (Clipboard = "") {
        ToolTip, No text selected!
        SetTimer, RemoveToolTip, 2000
        Clipboard := ClipSaved
        return
    }
    
    ; Extract phone number (digits only, max 12)
    selectedText := Clipboard
    phoneNumber := RegExReplace(selectedText, "\D")
    
    if (StrLen(phoneNumber) > 12) {
        phoneNumber := SubStr(phoneNumber, 1, 12)
    }
    
    if (StrLen(phoneNumber) < 7) {
        phoneNumber := RegExReplace(selectedText, "[^a-zA-Z0-9]")
        if (StrLen(phoneNumber) > 30) {
            phoneNumber := SubStr(phoneNumber, 1, 30)
        }
    }
    
    ; Generate onboarding message
    message := GenerateMessage(phoneNumber)
    
    ; Copy to clipboard
    Clipboard := message
    
    ; Show notification
    ToolTip, Message copied! Press Ctrl+V to paste.
    SetTimer, RemoveToolTip, 3000
    return
}

GenerateMessage(id) {
    global PORTAL_URL
    
    msg := "السلام عليكم ورحمة الله وبركاته.`n`n"
    msg .= "يسعدنا مساعدتكم في إطلاق حملتكم لجمع التبرعات عبر منصتنا. نحن بصدد إعداد بياناتكم الأولية.`n`n"
    msg .= "🛠 **بوابة التعديل السيادي (Sovereign Portal)**:`n"
    msg .= PORTAL_URL "#" id "`n`n"
    msg .= "يرجى استخدام هذا الرابط لمراجعة بياناتكم الأولية ورفع الصور والقصة الخاصة بكم.`n"
    msg .= "إذا لم يعمل الرابط المباشر، يمكنك الدخول إلى " PORTAL_URL " وإدخال رقم الواتساب الخاص بك المكون من رمز الدولة ثم الرقم (بدون + أو مسافات).`n`n"
    msg .= "الـ ID الخاص بكم هو: " id "`n`n"
    msg .= "سيتم ربط حملتكم بمحفظة رقمية لضمان وصول المساعدة كاملة وبأمان.`n`n"
    msg .= "------------------------------`n`n"
    msg .= "Salam Alaykum.`n`n"
    msg .= "We are honored to help you launch your fundraising campaign. We are setting up your initial profile.`n`n"
    msg .= "🛠 **Sovereign Portal**:`n"
    msg .= PORTAL_URL "#" id "`n`n"
    msg .= "Use this link to verify your details and upload your photos and story.`n"
    msg .= "If the direct link doesn't work, you can go to " PORTAL_URL " and enter your WhatsApp number (Country code + number, no + or spaces).`n`n"
    msg .= "Your ID is: " id "`n`n"
    msg .= "Your campaign will be linked to a digital wallet to ensure aid reaches you fully and securely.`n"
    
    return msg
}

RemoveToolTip:
    SetTimer, RemoveToolTip, Off
    ToolTip
    return

; Exit hotkey Ctrl+Alt+Q
^!q::
    MsgBox, Onboarding Assistant stopped.
    ExitApp
    return
