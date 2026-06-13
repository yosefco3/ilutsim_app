---
name: md-to-pdf
description: Convert a Markdown file into a styled, print-ready PDF — RTL Hebrew by default, with colored headers, boxed blockquotes, and styled tables. Use whenever the user asks to turn a Markdown doc into a PDF, regenerate a PDF from its Markdown source, or produce a Hebrew/RTL PDF report. No heavy deps — uses system python3-markdown + LibreOffice headless.
user-invocable: true
---

# Markdown → PDF

Renders Markdown to a polished PDF via **Markdown → styled HTML → LibreOffice headless**.
Chosen because it needs no extra Python PDF libraries (only the system
`python3-markdown`) and produces clean **RTL Hebrew** with proper fonts.

## Usage

```bash
python3 .claude/skills/md-to-pdf/md_to_pdf.py INPUT.md [-o OUTPUT.pdf] [--ltr] [--title "..."]
```

- Default layout is **RTL** (Hebrew). Pass `--ltr` for left-to-right docs.
- Default output is the input path with a `.pdf` extension; override with `-o`.
- **Hard page break:** put `@@PAGEBREAK@@` on its own line in the Markdown.

Example — rebuild the managers' review doc in this repo:

```bash
python3 scripts/build_managers_pdf.py          # thin wrapper around this skill
# or directly:
python3 .claude/skills/md-to-pdf/md_to_pdf.py COMBINED_FOR_MANAGERS.md \
  -o מערכת_ניהול_משמרות_סקירה_ותכנון.pdf
```

## What it produces

- Indigo headings (`#3b3b7a`) with underline rules.
- Boxed blockquotes (lavender background, accent border on the start side).
- Tables with an indigo header row and zebra striping.
- Hebrew font stack: **Noto Sans Hebrew → Noto Sans → DejaVu Sans**.

## Requirements

- `python3-markdown` (system package; import name `markdown`).
- `libreoffice` / `soffice` on PATH (used headless).
- A Hebrew-capable font installed (e.g. `fonts-noto` provides *Noto Sans Hebrew*).

## Customizing the look

Edit `CSS_TEMPLATE` in `md_to_pdf.py`. It is a `str.format` template with
`{direction}`, `{align}`, and `{startside}` placeholders so the same stylesheet
serves both RTL and LTR. The `convert(src, out, rtl=, title=)` function is also
importable from other scripts.

## Notes / gotchas

- Numbers and Latin runs inside RTL text follow the Unicode bidi algorithm, so
  long digit strings (phone numbers) may render with spacing that looks
  "reversed" — this is expected RTL behavior, not a bug.
- LibreOffice must be able to launch headless; on a fresh machine the first run
  can be slow while it initializes its profile.
