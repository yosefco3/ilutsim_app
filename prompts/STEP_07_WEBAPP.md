# Step 7 — Telegram Web App (Frontend — Constraint Submission Form) & Tests

## Context
You are continuing development of the Micro-SaaS security guard shift constraint management system. **Steps 0-6 (full backend + Telegram bot) are complete. All previous tests pass.**

**Important:** All user-facing text is in **Hebrew only**. The entire UI is RTL. Code comments in English.

## Objective
Build the Telegram Web App — a React SPA that runs inside Telegram, providing the weekly constraint submission form with day-by-day availability, shift selection, blocked date handling, read-only mode, and Upsert (prefill) support. Write component and hook tests.

## Technology
- React 18 with Vite
- Vitest + React Testing Library for tests
- No external UI library (custom CSS, Telegram theme variables)

## File Structure

```
frontend/webapp/
├── index.html
├── vite.config.js
├── package.json
├── .env.example                    # VITE_API_URL=http://localhost:8000
├── src/
│   ├── main.jsx                    # React root mount
│   ├── App.jsx                     # Main app wrapper
│   ├── api/
│   │   └── apiClient.js            # Fetch wrapper with Telegram initData auth
│   ├── components/
│   │   ├── WeekForm.jsx            # Main form: 7 day cards + notes + submit
│   │   ├── DayCard.jsx             # Single day: toggle + shift checkboxes
│   │   ├── ShiftCheckbox.jsx       # Shift type toggle with time inputs
│   │   ├── BlockedDay.jsx          # Disabled day (vacation/military/training)
│   │   ├── LockBanner.jsx          # Read-only banner when week is locked
│   │   ├── NotesField.jsx          # General notes textarea
│   │   ├── LoadingSpinner.jsx      # Loading indicator
│   │   └── ErrorMessage.jsx        # Error display component
│   ├── hooks/
│   │   ├── useSubmission.js        # Data fetching, state management, form submit
│   │   └── useTelegram.js          # Telegram WebApp SDK integration
│   ├── utils/
│   │   └── messages.js             # ALL Hebrew UI texts centralized here
│   └── styles/
│       └── main.css                # Mobile-first, RTL, Telegram theme colors
├── __tests__/
│   ├── setup.js                    # Test setup (jsdom, Telegram SDK mock)
│   ├── WeekForm.test.jsx
│   ├── DayCard.test.jsx
│   ├── ShiftCheckbox.test.jsx
│   ├── BlockedDay.test.jsx
│   ├── LockBanner.test.jsx
│   ├── useSubmission.test.js
│   └── apiClient.test.js
```

## Detailed Requirements

### 1. `useTelegram.js` — Telegram SDK Hook
```javascript
export function useTelegram() {
    // Access window.Telegram.WebApp
    // Return: { initData, user, themeParams, mainButton, close }
    // initData: string for API auth
    // user: { id, first_name, last_name } from initDataUnsafe
    // themeParams: color scheme
    // mainButton: Telegram MainButton API (show/hide/setText/onClick)
    // close: Telegram.WebApp.close()
}
```

### 2. `apiClient.js` — API Communication
- Every request includes `Authorization: Bearer <initData>` header
- Base URL from `import.meta.env.VITE_API_URL`
- Methods: `get(path)`, `post(path, body)`
- Global error handling:
  - 401 → display auth error (from messages.js)
  - 403 → display lock error (from messages.js)
  - 422 → display validation error
  - 500 → display generic error
- Returns `{ data, error }` tuple pattern

### 3. `useSubmission.js` — Core Data Hook
```javascript
export function useSubmission(weekId) {
    // State: loading, error, submission, blockedDates, defaults, isReadOnly
    
    // On mount: fetch all 3 in parallel (Promise.all):
    //   GET /api/submissions/{weekId}         → existing submission (prefill)
    //   GET /api/submissions/{weekId}/blocked-dates  → blocked dates
    //   GET /api/submissions/{weekId}/defaults       → default times + week status
    
    // Initialize form state:
    //   If existing submission → prefill all days/shifts
    //   If no submission → initialize 7 empty days with defaults
    //   Mark blocked dates
    //   Set isReadOnly if week status != 'open'
    
    // submitForm(formData):
    //   POST /api/submissions
    //   On success → Telegram.WebApp.close()
    //   On error → set error state
    
    return { loading, error, days, setDays, blockedDates, defaults, isReadOnly, submitForm }
}
```

### 4. `WeekForm.jsx` — Main Form Component
- Renders 7 `DayCard` components in chronological order (Sunday → Saturday)
- Hebrew day names (from messages.js): יום ראשון, יום שני, ... , שבת
- If `isReadOnly` → show `LockBanner` + disable all inputs
- `NotesField` at the bottom
- Submit button uses Telegram MainButton (native) or fallback HTML button
- On submit: collect all day data → call `submitForm()`

### 5. `DayCard.jsx`
Props: `day`, `date`, `isAvailable`, `shifts`, `isBlocked`, `blockReason`, `isReadOnly`, `onChange`

- If blocked → render `BlockedDay` instead
- Toggle switch: "זמין" / "לא זמין" (from messages.js)
- When available: show 3 `ShiftCheckbox` components (morning, afternoon, night)
- When unavailable: hide shift checkboxes
- Display: Hebrew day name + formatted date

### 6. `ShiftCheckbox.jsx`
Props: `shiftType`, `label`, `isChecked`, `startTime`, `endTime`, `defaultStart`, `defaultEnd`, `isReadOnly`, `onChange`

- Checkbox with label (messages.js: "בוקר" / "צהריים" / "לילה")
- When checked: show two `<input type="time">` — "משעה" and "עד שעה"
- Default values from `defaults` (API response)
- When unchecked: hide time inputs

### 7. `BlockedDay.jsx`
Props: `dayName`, `date`, `eventType`, `label`

- Rendered as a grayed-out card
- Shows: day name + "חסום — {label}" (e.g., "חסום — מילואים")
- All interactions disabled
- Distinct visual style (gray background, strikethrough or opacity)

### 8. `LockBanner.jsx`
Props: `message`

- Fixed banner at top of form
- Text from messages.js (e.g., "השבוע נעול — לא ניתן לעדכן אילוצים")
- Visually prominent (yellow/orange background)

### 9. `NotesField.jsx`
Props: `value`, `onChange`, `isReadOnly`

- `<textarea>` with placeholder from messages.js
- Label: "הערות כלליות"

### 10. Submit Payload Format
```json
{
    "week_id": "uuid",
    "general_notes": "text or null",
    "days": [
        {
            "date": "2024-01-07",
            "is_available": true,
            "shifts": [
                { "shift_type": "morning", "start_time": "07:00", "end_time": "15:00" },
                { "shift_type": "night", "start_time": "23:00", "end_time": "07:00" }
            ]
        },
        {
            "date": "2024-01-08",
            "is_available": false,
            "shifts": []
        }
    ]
}
```

### 11. `messages.js` — Frontend Hebrew Texts
```javascript
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
    LABEL_AFTERNOON: "צהריים",
    LABEL_NIGHT: "לילה",
    LABEL_FROM: "משעה",
    LABEL_TO: "עד שעה",
    LABEL_NOTES: "הערות כלליות",
    LABEL_NOTES_PLACEHOLDER: "הערות נוספות (אופציונלי)...",
    LABEL_BLOCKED: "חסום",
    LABEL_SUBMIT: "שלח אילוצים",
    LABEL_LOADING: "טוען...",
    LOCK_BANNER: "השבוע נעול — לא ניתן לעדכן אילוצים",
    ERR_AUTH: "שגיאת אימות — נסה שוב דרך הבוט",
    ERR_LOCKED: "השבוע נעול להגשות",
    ERR_GENERIC: "אירעה שגיאה — נסה שוב",
    ERR_NETWORK: "בעיית תקשורת — בדוק את החיבור לאינטרנט",
    SUCCESS_SUBMITTED: "האילוצים נשלחו בהצלחה!",
    EVENT_VACATION: "חופשה",
    EVENT_MILITARY: "מילואים",
    EVENT_FIREARMS: "רענון נשק",
};
```

### 12. `main.css` — Styling
- `direction: rtl; text-align: right;` on body
- Mobile-first (max-width: 100vw)
- Telegram theme CSS variables: `var(--tg-theme-bg-color)`, `var(--tg-theme-text-color)`, `var(--tg-theme-button-color)`, etc.
- Day cards: rounded corners, subtle shadow, spacing
- Blocked days: gray background, reduced opacity
- Lock banner: yellow/orange background, bold text
- Shift checkboxes: clear toggle style
- Time inputs: inline, compact
- Accessible: proper labels, focus states, sufficient contrast

## Tests Required (`__tests__/`)

### `WeekForm.test.jsx`
1. Renders 7 day cards for a full week
2. Renders notes field
3. Shows lock banner when `isReadOnly=true`
4. Hides submit button when `isReadOnly=true`
5. Calls submitForm with correct payload on submit

### `DayCard.test.jsx`
6. Toggles between available and unavailable
7. Shows 3 shift checkboxes when available
8. Hides shift checkboxes when unavailable
9. Displays Hebrew day name correctly

### `ShiftCheckbox.test.jsx`
10. Shows time inputs when checked
11. Hides time inputs when unchecked
12. Initializes with default times from props
13. Allows time editing

### `BlockedDay.test.jsx`
14. Renders as disabled (no interactive elements)
15. Shows correct event type label in Hebrew
16. Click does nothing (no state change)

### `LockBanner.test.jsx`
17. Renders with correct Hebrew message
18. Visible when passed as prop
19. Has correct visual styling (can check class/style)

### `useSubmission.test.js`
20. Fetches 3 endpoints on mount
21. Sets loading state correctly
22. Handles API errors gracefully
23. Submits form data in correct format

### `apiClient.test.js`
24. Adds Authorization header with initData to all requests
25. Handles 401 errors correctly
26. Handles 403 errors correctly
27. Uses base URL from environment

## Rules
- Zero hard-coded Hebrew text — everything from `messages.js`
- Zero hard-coded URLs — everything from environment variables
- Full error handling on client side
- Loading states for every API call
- Accessible HTML (labels, aria attributes)
- Mobile-first responsive design
- RTL layout throughout
- All tests must pass with `npm test`
- Code comments in English
