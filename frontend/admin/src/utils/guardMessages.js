/**
 * Centralized Hebrew UI texts for the guard-facing area.
 * Zero hard-coded Hebrew text elsewhere — everything comes from here.
 */
export const messages = {
  DAY_SUNDAY: "יום ראשון",
  DAY_MONDAY: "יום שני",
  DAY_TUESDAY: "יום שלישי",
  DAY_WEDNESDAY: "יום רביעי",
  DAY_THURSDAY: "יום חמישי",
  DAY_FRIDAY: "יום שישי",
  DAY_SATURDAY: "שבת",

  LABEL_AVAILABLE: "זמין",
  LABEL_UNAVAILABLE: "לא זמין",
  LABEL_MORNING: "בוקר",
  LABEL_AFTERNOON: "ערב",
  LABEL_NIGHT: "לילה",
  LABEL_FROM: "משעה",
  LABEL_TO: "עד שעה",
  LABEL_NOTES: "הערות כלליות",
  LABEL_NOTES_PLACEHOLDER: "הערות נוספות (אופציונלי)...",
  LABEL_BLOCKED: "חסום",
  LABEL_SUBMIT: "שלח אילוצים",
  LABEL_LOADING: "טוען...",

  LOCK_BANNER: "השבוע נעול — לא ניתן לעדכן אילוצים",
  LOCK_STATUS_CLOSED: "השבוע טרם נפתח להגשה",
  LOCK_STATUS_LOCKED: "ההגשה נסגרה — לא ניתן עוד לעדכן אילוצים",
  LOCK_STATUS_PUBLISHED: "סידור העבודה כבר פורסם",
  LOCK_NO_WEEK: "אין שבוע פעיל",

  ERR_AUTH: "שגיאת אימות — נסה שוב דרך הבוט",
  ERR_LOCKED: "השבוע נעול להגשות",
  ERR_GENERIC: "אירעה שגיאה — נסה שוב",
  ERR_NETWORK: "בעיית תקשורת — בדוק את החיבור לאינטרנט",
  SUCCESS_SUBMITTED: "האילוצים נשלחו בהצלחה!",
};

/** Day names in order Sunday–Saturday */
export const DAY_NAMES = [
  messages.DAY_SUNDAY,
  messages.DAY_MONDAY,
  messages.DAY_TUESDAY,
  messages.DAY_WEDNESDAY,
  messages.DAY_THURSDAY,
  messages.DAY_FRIDAY,
  messages.DAY_SATURDAY,
];

/** Map shift_type key to Hebrew label */
export const SHIFT_LABELS = {
  morning: messages.LABEL_MORNING,
  afternoon: messages.LABEL_AFTERNOON,
  night: messages.LABEL_NIGHT,
};

/**
 * Default shift hours — used as fallback when the API is unreachable.
 * Editable by admin via /admin/settings page (stored in DB).
 * Format: { shift_type: { from_hour, to_hour } }
 */
export const SHIFT_DEFAULTS = {
  morning: { from_hour: "07:00", to_hour: "16:30" },
  afternoon: { from_hour: "15:00", to_hour: "23:00" },
  night: { from_hour: "23:00", to_hour: "07:00" },
};
