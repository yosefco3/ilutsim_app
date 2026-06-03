"""
Centralized Hebrew messages for the entire application.
ALL Hebrew text must live here — no Hebrew strings outside this file.
"""


class Messages:
    """Container for all Hebrew text constants used in the system."""

    # ── Bot messages ──────────────────────────────────────────────────
    BOT_WELCOME: str = "שלום! 👋\nברוכים הבאים למערכת ניהול המשמרות.\nאנא שתפו את מספר הטלפון שלכם לצורך אימות."
    BOT_SHARE_CONTACT_BUTTON: str = "📱 שתף מספר טלפון"
    BOT_AUTH_SUCCESS: str = "✅ אימות הצליח! ברוכים הבאים למערכת."
    BOT_AUTH_FAIL: str = "❌ מספר הטלפון לא נמצא במערכת. אנא פנה למנהל."
    BOT_WEEK_OPEN: str = "📢 חלון הגשת האילוצים נפתח!\nאנא הגישו את האילוצים שלכם לשבוע הקרוב."
    BOT_REMINDER: str = "⏰ תזכורת: טרם הגשת את האילוצים שלך לשבוע הקרוב.\nהחלון ייסגר בקרוב!"
    BOT_SUBMISSION_SUMMARY: str = "📋 סיכום הגשה:\nשם: {name}\nאילוצים: {constraints}\nסטטוס: {status}"
    BOT_DEVIATION_WARNING: str = "⚠️ התראת חריגה:\n{name} — {deviation}\nימים חריגים: {days}"
    BOT_LOCKOUT: str = "🔒 השבוע נעול — לא ניתן להגיש אילוצים."
    BOT_SUBMIT_ANYWAY: str = "🔓 באפשרותך להגיש בכל זאת (עקיפת מנעול):"
    BOT_OPEN_WEBAPP_BUTTON: str = "🖥️ פתח את אפליקציית האילוצים"

    # ── Error messages ────────────────────────────────────────────────
    ERR_WEEK_LOCKED: str = "השבוע נעול, לא ניתן להגיש"
    ERR_USER_NOT_FOUND: str = "משתמש לא נמצא"
    ERR_USER_DEACTIVATED: str = "חשבון המשתמש מושבת"
    ERR_AUTH_FAILED: str = "אימות נכשל"
    ERR_CONFLICT: str = "התנגשות שינויים — נסה שוב"
    ERR_VALIDATION: str = "שגיאת אימות נתונים"

    # ── UI Labels ─────────────────────────────────────────────────────
    LABEL_AVAILABLE: str = "זמין"
    LABEL_UNAVAILABLE: str = "לא זמין"
    LABEL_BLOCKED: str = "חסום"
    LABEL_MORNING: str = "בוקר"
    LABEL_AFTERNOON: str = "צהריים"
    LABEL_NIGHT: str = "לילה"

    # ── Excel export labels ───────────────────────────────────────────
    EXCEL_HEADER_NAME: str = "שם"
    EXCEL_HEADER_PHONE: str = "טלפון"
    EXCEL_HEADER_NOTES: str = "הערות"
    EXCEL_HEADER_THRESHOLDS: str = "סף מינימום"
    EXCEL_HEADER_DEVIATION: str = "חריגה"
    EXCEL_REPORT_TITLE: str = "דוח משמרות — {start} עד {end}"

    # ── Event type labels ─────────────────────────────────────────────
    EVENT_VACATION: str = "חופשה"
    EVENT_MILITARY: str = "מילואים"
    EVENT_FIREARMS: str = "רענון נשק"

    # ── Submission status labels ──────────────────────────────────────
    STATUS_SUBMITTED: str = "הוגש"
    STATUS_SUBMITTED_VARIANCE: str = "הוגש עם חריגה"
    STATUS_PENDING: str = "ממתין להגשה"
    STATUS_AUTO_ABSENCE: str = "העדרות אוטומטית"