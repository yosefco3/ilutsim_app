# Step 8 — Admin Dashboard (Frontend) & Tests

## Context
You are continuing development of the Micro-SaaS security guard shift constraint management system. **Steps 0-7 (full backend + bot + Web App) are complete. All previous tests pass.**

**Important:** All user-facing text is in **Hebrew only**. The entire UI is RTL. Code comments in English.

## Objective
Build the Admin Dashboard — a React SPA for the security officer to manage guards, weeks, blockout events, track submissions, send reminders, configure settings, and export Excel reports. Write component tests.

## Technology
- React 18 with Vite + React Router v6
- Vitest + React Testing Library for tests
- No external UI library (custom CSS)

## File Structure

```
frontend/admin/
├── index.html
├── vite.config.js
├── package.json
├── .env.example                    # VITE_API_URL
├── src/
│   ├── main.jsx
│   ├── App.jsx                     # Router setup with Navbar
│   ├── api/
│   │   └── adminApiClient.js       # Fetch wrapper with admin API key auth
│   ├── pages/
│   │   ├── LoginPage.jsx           # Admin login (email + password)
│   │   ├── GuardsPage.jsx          # CRUD guards
│   │   ├── WeeksPage.jsx           # Manage weeks + status
│   │   ├── EventsPage.jsx          # Blockout events
│   │   ├── SubmissionsPage.jsx     # Track submissions + send reminders
│   │   ├── SettingsPage.jsx        # System settings (default shift times)
│   │   └── ExportPage.jsx          # Excel export
│   ├── components/
│   │   ├── ProtectedRoute.jsx      # Auth guard wrapper
│   │   ├── GuardForm.jsx           # Create/edit guard form (modal)
│   │   ├── GuardTable.jsx          # Guards data table
│   │   ├── WeekStatusControl.jsx   # Status change buttons with confirm
│   │   ├── StatusGrid.jsx          # Submission status grid table
│   │   ├── EventForm.jsx           # Create blockout event form
│   │   ├── ConfirmDialog.jsx       # Confirmation dialog for destructive actions
│   │   └── Navbar.jsx              # Top navigation bar with logout
│   ├── hooks/
│   │   ├── useGuards.js            # Guards CRUD operations
│   │   ├── useWeeks.js             # Weeks operations
│   │   ├── useSubmissions.js       # Submissions tracking
│   │   └── useSettings.js          # Settings operations
│   ├── utils/
│   │   └── messages.js             # ALL Hebrew UI texts centralized here
│   └── styles/
│       └── admin.css               # Admin-specific styles
├── __tests__/
│   ├── setup.js
│   ├── LoginPage.test.jsx
│   ├── GuardsPage.test.jsx
│   ├── WeeksPage.test.jsx
│   ├── SubmissionsPage.test.jsx
│   ├── StatusGrid.test.jsx
│   ├── GuardForm.test.jsx
│   └── ConfirmDialog.test.jsx
```

## Detailed Requirements

### 1. `adminApiClient.js` — API Client
- On login: store JWT token in `localStorage` (key: `admin_token`)
- Every request includes `Authorization: Bearer <jwt_token>` header
- Base URL from `import.meta.env.VITE_API_URL`
- Methods: `get(path)`, `post(path, body)`, `put(path, body)`, `patch(path, body)`, `del(path)`
- For Excel download: `downloadFile(path)` — triggers browser file download
- Auto-redirect to `/login` on 401 responses (token expired)
- Methods: `login(email, password)`, `logout()` (clears token), `isAuthenticated()` (checks token exists)
- Error handling: toast/alert for errors

### 2. `App.jsx` — Router with Auth Guard
```
Routes:
  /login           → LoginPage (public, no auth needed)
  /                → Protected routes (requires valid JWT):
    /submissions   → SubmissionsPage (default/home)
    /guards        → GuardsPage
    /weeks         → WeeksPage
    /events        → EventsPage
    /settings      → SettingsPage
    /export        → ExportPage
```
Default redirect to `/submissions` for authenticated users, `/login` for unauthenticated.

**Auth flow:**
- On app load: check if JWT exists in localStorage
- If no token → redirect to `/login`
- If token exists → validate by calling `GET /api/auth/me`
- If 401 → clear token, redirect to `/login`
- Wrap protected routes in a `ProtectedRoute` component that checks auth state

### 3. `LoginPage.jsx` — Admin Login
- Email input field (label: "אימייל")
- Password input field (label: "סיסמה")
- "התחבר" (Login) button
- On submit: `POST /api/auth/login` with `{email, password}`
- On success: store JWT token in localStorage, redirect to `/submissions`
- On error: show Hebrew error message ("אימייל או סיסמה שגויים")
- If current admin is `super_admin`: show "הוסף מנהל" (Add Admin) link

### 4. `Navbar.jsx`
- Horizontal navigation bar with links to all pages
- Hebrew labels from messages.js
- Active page highlighted
- App title: "מערכת ניהול משמרות" (from messages.js)
- **Top-right corner:** Show logged-in admin name + role badge
- **"התנתק" (Logout) button:** clears token, redirects to `/login`

### Pages

### 5. `GuardsPage.jsx`
- `GuardTable`: displays all guards in a table
  - Columns: שם | טלפון | תפקיד | סטטוס | Telegram | סף כללי | סף לילה | סף ערב | פעולות
  - Status: פעיל (green badge) / מושבת (red badge)
  - Telegram: ✅ (linked) / ❌ (not linked)
  - Actions: עריכה button, השבתה button
- "הוסף שומר" button → opens `GuardForm` modal
- Edit button → opens `GuardForm` modal prefilled
- Deactivate button → `ConfirmDialog` → PATCH deactivate

### 6. `GuardForm.jsx` (Modal)
Fields:
- שם מלא (required)
- טלפון (required, Israeli phone validation)
- תפקיד (dropdown: שומר / קב"ט / סורק) — labels from messages.js
- הערות פטורים (textarea, optional)
- סף משמרות כללי (number, default 0)
- סף משמרות לילה (number, default 0)
- סף משמרות ערב (number, default 0)

Validation:
- Phone format validation (Israeli)
- Name required
- Show inline Hebrew error messages

### 7. `WeeksPage.jsx`
- List of weeks: cards or table rows
  - Each: start_date — end_date | status badge (פתוח/נעול/פורסם)
- "צור שבוע חדש" button → date pickers for start + end
- `WeekStatusControl` for each week:
  - Buttons: פתוח → נעול → פורסם (progressive flow)
  - Each transition requires `ConfirmDialog`
  - Disabled states for invalid transitions

### 8. `EventsPage.jsx`
- Dropdown: select guard (from guard list)
- `EventForm`:
  - Event type dropdown: חופשה / מילואים / רענון נשק (from messages.js)
  - Start date + End date pickers
  - Submit button
- Events list (filtered by selected guard):
  - Type | Start | End | Delete button
  - Delete → `ConfirmDialog`

### 9. `SubmissionsPage.jsx` — Main Dashboard Page
- Dropdown: select week
- Counter bar: "הגישו X מתוך Y" (submitted X of Y)
- `StatusGrid` table:
  - Columns: שומר | סטטוס | תאריך הגשה | חריגה
  - Status with color-coded icons:
    - "הוגש ✅" (green)
    - "הוגש עם חריגה ⚠️" (orange)
    - "ממתין להגשה 🔴" (red)
    - "העדרות אוטומטית 📋" (gray)
  - Sortable by status
- "שלח תזכורת" button:
  - Only sends to users with "ממתין להגשה" status
  - `ConfirmDialog`: "לשלוח תזכורת ל-X שומרים?"
  - After sending: show success/failure feedback with count

### 10. `SettingsPage.jsx`
- Form with 6 time inputs:
  - בוקר: משעה / עד שעה
  - צהריים: משעה / עד שעה
  - לילה: משעה / עד שעה
- Save button → PUT API
- Success feedback

### 11. `ExportPage.jsx`
- Dropdown: select week
- "הורד Excel" button → triggers file download
- Loading indicator during download

### 11. `ConfirmDialog.jsx`
Props: `isOpen`, `title`, `message`, `confirmText`, `cancelText`, `onConfirm`, `onCancel`, `isDestructive`

- Modal overlay
- Title + message in Hebrew
- Two buttons: confirm (red if destructive) + cancel
- Closes on backdrop click or cancel
- All text from messages.js

### 13. `messages.js` — Admin Hebrew Texts
```javascript
export const messages = {
    APP_TITLE: "מערכת ניהול משמרות",
    NAV_GUARDS: "שומרים",
    NAV_WEEKS: "שבועות",
    NAV_EVENTS: "אירועי חסימה",
    NAV_SUBMISSIONS: "מעקב הגשות",
    NAV_SETTINGS: "הגדרות",
    NAV_EXPORT: "ייצוא",
    
    // Auth
    LOGIN_TITLE: "התחברות מנהלים",
    LOGIN_EMAIL: "אימייל",
    LOGIN_PASSWORD: "סיסמה",
    LOGIN_BUTTON: "התחבר",
    LOGIN_ERROR: "אימייל או סיסמה שגויים",
    LOGIN_EMAIL_REQUIRED: "נא להזין אימייל",
    LOGIN_PASSWORD_REQUIRED: "נא להזין סיסמה",
    LOGOUT: "התנתק",
    ADMIN_ROLE_SUPER: "מנהל על",
    ADMIN_ROLE_ADMIN: "מנהל",
    ADMIN_ROLE_VIEWER: "צופה",
    ADMIN_ADD: "הוסף מנהל",
    ADMIN_ADD_TITLE: "הוספת מנהל חדש",
    
    // Guards
    GUARDS_TITLE: "ניהול שומרים",
    GUARD_ADD: "הוסף שומר",
    GUARD_EDIT: "עריכת שומר",
    GUARD_NAME: "שם מלא",
    GUARD_PHONE: "טלפון",
    GUARD_ROLE: "תפקיד",
    GUARD_STATUS: "סטטוס",
    GUARD_ACTIVE: "פעיל",
    GUARD_INACTIVE: "מושבת",
    GUARD_TELEGRAM: "Telegram",
    GUARD_THRESHOLD_TOTAL: "סף כללי",
    GUARD_THRESHOLD_NIGHT: "סף לילה",
    GUARD_THRESHOLD_EVENING: "סף ערב",
    GUARD_EXEMPTIONS: "הערות פטורים",
    GUARD_DEACTIVATE: "השבת שומר",
    GUARD_DEACTIVATE_CONFIRM: "האם להשבית את {name}?",
    
    ROLE_GUARD: "שומר",
    ROLE_SHIFT_LEAD: "קב\"ט",
    ROLE_SCANNER: "סורק",
    
    // Weeks
    WEEKS_TITLE: "ניהול שבועות",
    WEEK_CREATE: "צור שבוע חדש",
    WEEK_START: "תאריך התחלה",
    WEEK_END: "תאריך סיום",
    WEEK_STATUS_OPEN: "פתוח",
    WEEK_STATUS_LOCKED: "נעול",
    WEEK_STATUS_PUBLISHED: "פורסם",
    WEEK_LOCK_CONFIRM: "האם לנעול את השבוע? לא יהיה ניתן להגיש אילוצים.",
    WEEK_PUBLISH_CONFIRM: "האם לפרסם את השבוע?",
    
    // Events
    EVENTS_TITLE: "אירועי חסימה",
    EVENT_ADD: "הוסף אירוע",
    EVENT_TYPE: "סוג אירוע",
    EVENT_VACATION: "חופשה",
    EVENT_MILITARY: "מילואים",
    EVENT_FIREARMS: "רענון נשק",
    EVENT_DELETE_CONFIRM: "האם למחוק את האירוע?",
    
    // Submissions
    SUBMISSIONS_TITLE: "מעקב הגשות",
    SUBMISSIONS_COUNTER: "הגישו {submitted} מתוך {total}",
    SUBMISSIONS_SEND_REMINDER: "שלח תזכורת",
    SUBMISSIONS_REMINDER_CONFIRM: "לשלוח תזכורת ל-{count} שומרים?",
    SUBMISSIONS_REMINDER_SUCCESS: "נשלחו {sent} תזכורות",
    STATUS_SUBMITTED: "הוגש ✅",
    STATUS_VARIANCE: "הוגש עם חריגה ⚠️",
    STATUS_PENDING: "ממתין להגשה 🔴",
    STATUS_AUTO_ABSENCE: "העדרות אוטומטית 📋",
    
    // Settings
    SETTINGS_TITLE: "הגדרות מערכת",
    SETTINGS_SHIFT_TIMES: "שעות ברירת מחדל למשמרות",
    SETTINGS_SAVE: "שמור",
    SETTINGS_SAVED: "ההגדרות נשמרו בהצלחה",
    
    // Export
    EXPORT_TITLE: "ייצוא דוח Excel",
    EXPORT_DOWNLOAD: "הורד Excel",
    EXPORT_SELECT_WEEK: "בחר שבוע",
    
    // Common
    BTN_SAVE: "שמור",
    BTN_CANCEL: "ביטול",
    BTN_DELETE: "מחק",
    BTN_CONFIRM: "אישור",
    BTN_ACTIONS: "פעולות",
    LOADING: "טוען...",
    ERR_GENERIC: "אירעה שגיאה",
    ERR_REQUIRED: "שדה חובה",
    ERR_PHONE_FORMAT: "מספר טלפון לא תקין",
};
```

## Tests Required (`__tests__/`)

### `LoginPage.test.jsx`
1. Renders email and password fields
2. Shows Hebrew error on empty submit
3. Calls login API on valid submit
4. Shows Hebrew error message on failed login
5. Redirects to /submissions on successful login

### `GuardsPage.test.jsx`
6. Renders guard table with mock data
7. Opens GuardForm modal on "add guard" click
8. Submits new guard via API (mock)
9. Deactivate button shows ConfirmDialog
10. Displays Telegram connection status (✅/❌)

### `WeeksPage.test.jsx`
11. Renders list of weeks with status badges
12. Creates new week with date inputs
13. Status change button shows ConfirmDialog
14. Status badges render with correct Hebrew text and color

### `SubmissionsPage.test.jsx`
15. Renders StatusGrid for selected week
16. Shows correct status icons per user
17. "Send reminder" button triggers API call
18. Displays counter "X of Y" correctly

### `StatusGrid.test.jsx`
19. Renders all 4 status types correctly
20. Highlights deviation rows
21. Sorts by status column

### `GuardForm.test.jsx`
22. Validates required fields (shows error on empty submit)
23. Validates phone format (shows error on invalid phone)
24. Submits valid data correctly
25. Shows inline error messages in Hebrew

### `ConfirmDialog.test.jsx`
26. Displays correct title and message
27. Calls onConfirm callback on confirm button click
28. Calls onCancel callback on cancel button click
29. Closes on backdrop click

## Rules
- RTL layout throughout
- Mobile responsive design
- All Hebrew text from `messages.js` — zero hard coding
- Error handling + loading states on every page
- `ConfirmDialog` before every destructive action (deactivate, delete, status change, send reminder)
- All tests must pass with `npm test`
- Code comments in English
