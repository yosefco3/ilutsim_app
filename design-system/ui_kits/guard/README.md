# Guard Mini-App — UI kit

A faithful recreation of the **guard-facing weekly availability form** — the screen a security guard opens inside Telegram (a Telegram Web App / Mini App) to report when they can work.

## Run
Open `index.html` (sized for a 480px mini-app column). Toggle any shift on a day to reveal its hours; press **שלח אילוצים** to see the success state; **עריכת ההגשה** returns to the form.

## What it shows
- 7 days (ראשון → שבת) × 3 shifts (בוקר / ערב / לילה), each an independent toggle with editable hours.
- Default hours auto-fill on toggle (morning 07:00–16:30, evening 15:00–23:00, night 23:00–07:00) and are editable.
- General-notes textarea + submit, and the post-submit success card.

## Visual world
This surface is deliberately **separate from the dark admin theme**. It follows Telegram's runtime theme: light background, Telegram-blue actions. It uses the `--tg-*` tokens from `../../styles.css` (which fall back to Telegram's injected `--tg-theme-*` variables in production), styled by `guard-kit.css` (ported from the live `guard.css`). It does **not** use the dark-indigo DS components.
