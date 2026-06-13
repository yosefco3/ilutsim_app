---
name: ilutsim-design
description: Use this skill to generate well-branded interfaces and assets for אילוצים (Ilutsim) — a Hebrew, RTL security-guard shift-scheduling product — for production or for throwaway prototypes/mocks. Contains the dark-indigo admin design system plus the Telegram guard mini-app: colors, type, fonts, spacing, the emoji icon approach, reusable components, and full UI-kit screen recreations.
user-invocable: true
---

Read the `README.md` file within this skill first — it covers product context, content fundamentals, visual foundations, iconography, and a full index/manifest. Then explore the other files as needed:

- `styles.css` + `tokens/*.css` — the design tokens (colors, type, spacing, fonts). Link `styles.css` to inherit everything.
- `components/**` — reusable React primitives (`Button`, `Badge`, `Card`, `Alert`, `Field`, `TextInput`, `Select`, `Textarea`, `Toast`, `Dialog`). Each has a `.prompt.md` with usage and a `.card.html` showing live states.
- `guidelines/*.card.html` — foundation specimens (colors, type, spacing, brand).
- `ui_kits/admin/**` — the dark-indigo admin dashboard (login, weeks, guards, submissions).
- `ui_kits/guard/**` — the light Telegram availability form.

Key rules to honor:
- **RTL Hebrew always.** Mirror layouts; keep copy plain and operational.
- **Two visual worlds:** dark-indigo admin vs. light Telegram guard side — don't mix them.
- **One indigo accent**, neutral everything else; soft tints for badges/alerts, solids for buttons.
- **Emoji are the icon system** — functional, one leading glyph, never decorative.
- **Warn, don't block** — surface rule violations as soft, informational banners.

If creating visual artifacts (slides, mocks, throwaway prototypes), copy assets out and create static HTML files for the user to view. If working on production code, copy assets and read the rules here to design as an expert in this brand.

If the user invokes this skill without other guidance, ask what they want to build or design, ask a few clarifying questions, and act as an expert designer who outputs HTML artifacts or production code, depending on the need.
