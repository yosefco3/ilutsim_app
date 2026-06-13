# Admin Dashboard — UI kit

A faithful, interactive recreation of the **אילוצים** admin dashboard (the security manager's web app). Dark-indigo, RTL Hebrew.

## Run
Open `index.html`. It boots on the **login** screen → enter anything → lands on **מאבטחים** (Guards). Use the navbar to move between screens; actions fire toasts and confirm dialogs.

## Screens
| File | Screen | Notes |
|------|--------|-------|
| `LoginScreen.jsx` | כניסת מנהל | Centered card on an indigo radial glow |
| `WeeksScreen.jsx` | ניהול שבועות | Week lifecycle cards — closed → open → locked → published, with status-specific actions + delete confirm |
| `GuardsScreen.jsx` | ניהול מאבטחים | Data table + add/edit form + delete confirm |
| `SubmissionsScreen.jsx` | דיווחים | Who submitted for the open week, expandable per-guard availability detail |
| `Navbar.jsx` | top bar | Gradient wordmark + nav links + logout |

`EmptyScreen` placeholders stand in for אירועים / ייצוא / הגדרות (present in the live app, not central to this kit).

## How it's built
- `kit.css` — structural layout classes (navbar, table, week cards, login) ported from the live `admin.css`, all referencing the design-system tokens in `../../styles.css`.
- `data.js` — mock Hebrew data mirroring the live API shapes.
- Buttons, badges, cards, alerts, inputs, selects, dialogs and toasts all come from the design-system components (`window.IlutsimDesignSystem_f4254f`), not re-implemented here.
