# Ilutsim Design System (אילוצים)

A design system for **אילוצים** ("Constraints") — a Hebrew, right-to-left system for managing **security-guard shift scheduling**. Guards submit their weekly availability (through a Telegram mini-app), and a security manager turns that availability into a published work schedule from a web admin dashboard.

This repository captures the product's two visual worlds — the **dark-indigo admin dashboard** and the **light, Telegram-themed guard mini-app** — as tokens, components, foundation specimens and interactive UI-kit recreations.

## Sources

Built by reading the product's own source. Explore these further for deeper fidelity:

- **GitHub:** `yosefco3/ilutsim_app` — https://github.com/yosefco3/ilutsim_app
  - `frontend/admin/src/styles/admin.css` — the dark-indigo admin design system (source of every token here).
  - `frontend/admin/src/styles/guard.css` — the Telegram guard area.
  - `frontend/admin/src/components/`, `…/pages/` — React components/screens recreated in the UI kits.
  - `frontend/admin/src/utils/messages.js`, `…/guardMessages.js` — the Hebrew copy.
  - `APP_OVERVIEW.md` — full product/architecture overview.
  - `SCHEDULING_FOR_MANAGERS.md` + `מערכת_ניהול_משמרות_סקירה_ותכנון.pdf` — the *planned* drag-and-drop schedule-builder (not yet built; see "What's intentionally not here").

The reader is assumed not to have access; everything needed to design in-brand lives in this repo.

---

## Product context

- **Two audiences, two surfaces.** The **security manager** uses a feature-dense dark admin dashboard (manage guards, run the week lifecycle, review submissions, export). The **guard** uses a tiny light form inside Telegram to submit availability.
- **The week is the unit of work.** Every week moves through a lifecycle: **סגור (closed) → פתוח (open) → נעול (locked) → פורסם (published)**. Each state has its own allowed actions.
- **Roles** (guards): אחמ"ש · מאבטח בסיסי · מאבטח רמה ב' · מאבטח 9 שעות · לא חמוש · בודק.
- **Shifts**: בוקר / ערב / לילה, each with default-but-editable hours.

---

## Content fundamentals

- **Language:** Hebrew, **RTL throughout**. Every layout, control and icon is mirrored. Latin text (codes, hours) sits inline naturally.
- **Voice:** plain, operational, second-person-implicit. Buttons are bare imperatives — **שמור**, **מחק**, **פתח להגשה**, **שלח אילוצים**. No marketing tone, no exclamation except the one genuine success ("האילוצים נשלחו בהצלחה!").
- **Labels over sentences.** Field labels and table heads are 1–2 words (שם מלא, תפקיד, סטטוס, תאריך הגשה). Hints are short and explanatory ("ניתן למלא ולערוך אילוצים בכל סטטוס שבוע").
- **The soft-warning principle.** A defining trait: the system **warns but does not block**. When availability or an assignment breaks a rule, it shows an informational banner ("שים לב — ייתכן שחרגת מהכללים (ניתן לשלוח בכל זאת)") and still allows the action. The manager / guard always decides. Carry this tone into anything new.
- **Confirmations** are blunt about irreversibility: "פעולה זו אינה ניתנת לביטול."
- **No em-dashes as decoration; no emoji in prose.** Emoji appear only as functional inline icons on buttons/badges (see Iconography).

---

## Visual foundations

- **Theme:** dark, layered, minimal — "Dark Indigo." The admin app is built on five stacked dark surfaces (`--bg` `#0f1115` → `--surface` → `--surface-2` → `--surface-3`, plus `--navbar-bg`), separated by two hairline border weights (`--border`, `--border-strong`) rather than heavy shadows.
- **Accent:** a single indigo (`--primary` `#6366f1`), used for primary actions, active nav, focus rings and the brand gradient. Restraint is the rule — one accent, everything else neutral.
- **Semantics:** danger / success / warning / info each exist as a solid color **and** a low-alpha "soft" tint. Badges and alerts use the soft tint with a matching light foreground (`--on-success` etc.); buttons use the solid.
- **Type:** the live app uses the platform system sans (Segoe UI / Tahoma). This system standardises on **Heebo** (Google Fonts) for portability — see *Font substitution* below. Scale runs 12 → 24px; weights lean on 550/650 micro-weights for controls and headings, 700 for the brand and day names.
- **Spacing:** a `0.25rem` rhythm (`--space-1`…`--space-10`). Card padding 20px, page gutters 24px, main column capped at 1100px; the guard column at 480px.
- **Radius:** 7px (controls/badges-as-rect), 10px (cards/tables/alerts), 14px (dialogs/login), 999px (status pills).
- **Elevation:** three dark shadows — `--shadow` (resting cards/tables), `--shadow-md` (hover lift on week cards), `--shadow-lg` (dialogs, toasts).
- **Borders define structure**, shadows are secondary. Cards = `--surface` + 1px `--border` + small shadow. Interactive cards brighten the border and lift to `--shadow-md` on hover.
- **Backgrounds:** flat dark fills only. The single gradient in the product is the brand wordmark (white→indigo, clipped to text); the login screen adds one subtle indigo radial glow. No imagery, no illustration, no texture.
- **Motion:** quick and functional — `.15s` color/border transitions, a `.05s` 1px press translate on buttons, a small `fadeIn` on page/card mount, and a slide-down for toasts. Nothing bounces; nothing loops.
- **States:** hover = lighter surface or brighter border (`rgba(255,255,255,.03–.05)` on transparent buttons). Press = 1px down-translate. Focus = `--primary` border + 3px `--primary-soft` glow. Disabled = 0.45 opacity.
- **Transparency / blur:** reserved for the modal scrim (`rgba(5,7,12,.65)` + 2px backdrop blur). Soft tints are alpha colors, not blur.
- **Guard side** inverts all of this: light Telegram theme, Telegram-blue (`--tg-btn` `#3390ec`) outlined toggles that fill when on, 8–10px radii. It follows Telegram's host theme rather than the dark brand.

---

## Iconography

- **The icon system is emoji.** There is no icon font and no SVG icon set in the product. Status and actions are labelled with native emoji placed inline before the text: 📅 week/date · 🔓 open · 🔒 locked · 📢 publish · ⏳ closed · 🟢 open-for-submission · 🗑️ delete · 📊 export/report · ✅/✓ success · ✕ error.
- **Usage:** sparing and functional only — one leading glyph per button or badge, never decorative clusters, never in body prose. The `Button` and `Badge` components take an `icon` prop for exactly this.
- **No logo mark.** The brand is the **wordmark** "אילוצים" / "ניהול מערכת אילוצים", set in Heebo Bold with a white→indigo gradient clipped to the text, shown only on dark surfaces.
- If a future surface needs true icons, add a CDN line-icon set (e.g. Lucide) at a 1.5–2px stroke and document it here — but match the current restraint first.

---

## What's intentionally *not* here

The **drag-and-drop schedule builder** (פרופילי הפעלה / עמדות / בניית הסידור) described in `SCHEDULING_FOR_MANAGERS.md` is a **plan, not a built screen** — so it is not recreated as a UI kit (kits replicate what exists). It is the natural next design exploration on top of this system. Ask, and we can design it in-brand: the position board, the availability-painting interaction, the auto-sorting guard list, and the soft warnings.

---

## Index / manifest

**Root**
- `styles.css` — the single entry point consumers link (imports the four token files below).
- `tokens/colors.css`, `tokens/typography.css`, `tokens/spacing.css`, `tokens/fonts.css`
- `README.md` (this file) · `SKILL.md`

**Components** (`window.IlutsimDesignSystem_f4254f`)
- `components/core/` — `Button`, `Badge`, `Card`, `Alert`
- `components/forms/` — `Field`, `TextInput`, `Select`, `Textarea`
- `components/feedback/` — `Toast`, `Dialog`

**Foundations** (`guidelines/` — specimen cards in the Design System tab)
- Colors: Surfaces · Indigo Accent · Semantic States · Text & Borders
- Type: Type Scale · Weights · Spacing: Spacing Scale · Radius & Elevation
- Brand: Wordmark · Iconography

**UI kits**
- `ui_kits/admin/` — the dark-indigo admin dashboard (login, weeks, guards, submissions) — interactive.
- `ui_kits/guard/` — the Telegram guard availability form — interactive.

## Font substitution

The live app ships **no webfont** — it renders in the host system sans (`'Segoe UI', Tahoma, …`). For consistent cross-device rendering this system substitutes **Heebo** (Google Fonts), the closest neutral Hebrew sans. **If you have a preferred brand font, send the files and we'll swap `tokens/fonts.css`.**
