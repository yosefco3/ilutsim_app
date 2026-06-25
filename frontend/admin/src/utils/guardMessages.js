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
  LABEL_SUBMITTING: "שולח...",
  LABEL_LOADING: "טוען...",

  LOCK_BANNER: "השבוע נעול — לא ניתן לעדכן אילוצים",
  LOCK_STATUS_CLOSED: "ההגשה סגורה כרגע",
  LOCK_STATUS_LOCKED: "השבוע נעול — ההגשה נסגרה ולא ניתן עוד לעדכן אילוצים",
  LOCK_STATUS_PUBLISHED: "סידור העבודה כבר פורסם",
  LOCK_NO_WEEK: "אין שבוע פעיל",

  ERR_AUTH: "שגיאת אימות — נסה שוב דרך הבוט",
  ERR_LOCKED: "השבוע נעול להגשות",
  ERR_GENERIC: "אירעה שגיאה — נסה שוב",
  ERR_NETWORK: "בעיית תקשורת — בדוק את החיבור לאינטרנט",
  // Shown when the POST returned 2xx but no persisted submission came back —
  // i.e. the server did not actually confirm the save. Never treat as success.
  ERR_NO_CONFIRM: "השרת לא אישר את ההגשה — נסה שוב",
  SUCCESS_SUBMITTED: "האילוצים נשלחו בהצלחה!",

  // Soft, non-blocking constraint-rule warnings (submission is still allowed).
  WARN_TITLE: "שים לב — ייתכן שחרגת מהכללים (ניתן לשלוח בכל זאת):",
  WARN_MIN_SHIFTS: (got, min) => `סימנת ${got} משמרות בלבד; המומלץ לפחות ${min}.`,
  WARN_MIN_NIGHTS: (got, min) => `סימנת ${got} לילות; המומלץ לפחות ${min}.`,
  WARN_MIN_EVENINGS: (got, min) => `סימנת ${got} ערבים; המומלץ לפחות ${min}.`,
  WARN_MAX_CONSEC: (got, max) => `סימנת ${got} ימים רצופים; המקסימום הוא ${max}.`,
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

/** Short day names (ראשון–שבת) for compact admin tables/headers. */
export const DAY_NAMES_SHORT = [
  "ראשון",
  "שני",
  "שלישי",
  "רביעי",
  "חמישי",
  "שישי",
  "שבת",
];

/** Shift type keys, in canonical daily order */
export const SHIFT_TYPES = ["morning", "afternoon", "night"];

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

/**
 * All half-hour time slots from "00:00" to "23:30" (48 values).
 * Used to populate the time dropdowns so guards/admins pick a value
 * instead of typing — no ":" to type, and only half-hour multiples are selectable.
 */
export const HALF_HOUR_OPTIONS = Array.from({ length: 48 }, (_, i) => {
  const h = String(Math.floor(i / 2)).padStart(2, "0");
  const m = i % 2 === 0 ? "00" : "30";
  return `${h}:${m}`;
});

/**
 * Half-hour slots ordered along the *security day*, which runs 07:00 → 07:00 the
 * next morning: 07:00, 07:30, … 23:30, 00:00, … 06:30. Used by the positions
 * editor so the dropdowns read in the order an admin thinks about a shift.
 * Index of "07:00" in HALF_HOUR_OPTIONS is 14 (7 * 2).
 */
export const DAY_HALF_HOUR_OPTIONS = [
  ...HALF_HOUR_OPTIONS.slice(14),
  ...HALF_HOUR_OPTIONS.slice(0, 14),
];
