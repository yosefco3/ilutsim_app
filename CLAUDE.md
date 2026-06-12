# Claude Code Custom Rules - ilutzim_app Project

> Mirror of `.clinerules`, adapted for Claude Code. Same limitations and workflows.

## Task Execution Strategy — Break Large Tasks into Small Steps

### When receiving a large feature request:
1. **Always propose breaking it into small, sequential steps** — each step touching 2-4 files max.
2. **Run tests after every step** — verify the step works before moving to the next.
3. **Present the full plan to the user before starting** — list all proposed steps, get approval, then execute one by one.
4. **Each step should be independently testable** — not just a partial implementation that leaves the app broken.
5. **Prefer many small commits over one large commit** — easier to review, revert, and debug.

### Why this matters:
- Bugs are caught early when each step is tested independently.
- Context window stays clean — each step focuses on a narrow scope.
- If something goes wrong, only the last step needs to be fixed.
- The user can review progress and adjust direction between steps.

## Step Budget — Soft Guardrail

> Adapted for Claude Code: no hard cap. Claude Code routinely needs many tool
> calls per task, so this is a checkpoint-and-reassess rule, not a stop-cold limit.

- There is **no fixed tool-use limit** — use as many tool calls as the task genuinely needs.
- But avoid silent spiraling: if you've used **~15 tool uses** and are still far from
  done, pause and report:
  - What was accomplished so far
  - What is blocking completion
  - Whether the current approach is working or should change
- Keep going only if you have a clear, justified path to completion. When in doubt, surface status and ask.

## Progress Checkpoints

- After every **5 tool uses**, append a one-line status to your response.
  Format: `[Step X/Y] Done: ... | Next: ...`
- This keeps the user informed and prevents silent spiraling.

## Think-Before-Act, Not Think-Instead-Of-Act

- Before using a tool, you may think for at most 2-3 sentences.
- If you need longer analysis, output it visibly as part of your response — do not hide it in internal reasoning.
- If you catch yourself thinking for more than 5 paragraphs, STOP and ask the user for direction.

## Code Review Graph — Mandatory Workflow

### After Every Coding Mission (when code files were created or modified):
1. **Update the code graph** — Run the CLI command:
   ```
   /home/yosef/.local/bin/code-review-graph update
   ```
   This performs an incremental update (only changed files) and is fast.
2. **Update APP_OVERVIEW.md** — If the change affects features, models, API endpoints, workflow, or architecture:
   - Add a new entry to the **היסטוריית שינויים משמעותיים** table at the bottom
   - Update relevant sections (models, endpoints, lifecycle, etc.) to reflect the change
   - Update the "עדכון אחרון" date at the top
   - Only skip if the change is purely internal (refactor, bug fix, test) with no user-facing impact.
3. Only skip graph update if NO source code files (.py, .js, .ts, etc.) were touched.

## Environment — Interpreter & Tool Paths (read this BEFORE running anything)

> There is **no `python` on PATH** — only `python3`. The backend deps (FastAPI,
> pytest, etc.) live in a virtualenv, NOT in the system python. Use these exact paths
> so you don't get stuck rediscovering them every session:

- **Backend Python (has all deps):** `backend/.venv/bin/python`
  - Run backend tests: `cd backend && .venv/bin/python -m pytest tests/ -q`
  - Or activate once: `source backend/.venv/bin/activate` then `python -m pytest ...`
  - ⚠️ `python scripts/test_graph.py` with bare/system python silently yields **0 backend results** — the script now auto-resolves `backend/.venv/bin/python` (see `backend_python()` in `scripts/test_graph.py`), so prefer running it as `python3 scripts/test_graph.py`.
- **Frontend tests:** `cd frontend/admin && npx vitest run`
- **Code-review graph CLI:** `/home/yosef/.local/bin/code-review-graph`

## Test Coverage — Mandatory Workflow

### After every significant change / feature:
1. **Update tests** — Add or update tests to cover the new/changed code.
2. **Run the test suite** — Single command:
   ```
   python3 scripts/test_graph.py
   ```
   This script does everything: runs all tests (backend + frontend), checks coverage, and generates a markdown report. It auto-uses `backend/.venv/bin/python` for the backend.
3. **One command instead of three** — No need to manually run pytest, vitest, and coverage separately.

### When to run:
- After completing a feature or significant change.
- Before committing final results.
- The script outputs results to `TEST_GRAPH.md` for easy review.

> **Graph tooling note:** This project uses the **`code-review-graph` CLI only**
> (see Graph CLI Reference below). The old `codegraph` MCP server has been removed
> — do **not** call `codegraph_*` MCP tools; they no longer exist here.

### When Starting a New Coding Task:
1. **Get minimal context first**:
   - `APP_OVERVIEW.md` to understand the app purpose, models, endpoints, and workflow.
   - `code-review-graph status` for a quick health/size check of the graph.
   - `_PROGRESS.md` if you are inside a prompts directory.
2. **To locate code**, use the standard search tools (`Grep`, `Glob`, `Read`) and the
   `code-review-graph` CLI. Keep `Grep` → `Read` chains tight and targeted.

### When Doing Code Review:
- Read `APP_OVERVIEW.md` for architecture/endpoint context.
- Use `Grep`/`Read` to trace callers/callees and understand blast radius before changing code.

### Graph CLI Reference:
- **Full rebuild:** `/home/yosef/.local/bin/code-review-graph build`
- **Incremental update:** `/home/yosef/.local/bin/code-review-graph update`
- **Post-process only:** `/home/yosef/.local/bin/code-review-graph postprocess`
- **Status check:** `/home/yosef/.local/bin/code-review-graph status`

## Prompt Library — Workflow

### When receiving a prompt library directory (e.g. `features-prompts/something/`):
1. **Check for `_PROGRESS.md`** in that directory — if it exists, read it to understand what's already done and where to continue.
2. **If `_PROGRESS.md` doesn't exist** — create an empty file. This means nothing has been done yet.
3. **Execute the next prompt file** (by number order: `01_...`, `02_...`, etc.).
4. **After successful completion** (tests pass, committed):
   - Append a summary line to `_PROGRESS.md`: what was done, files created/modified, commit message.
   - Delete the prompt file that was just executed.
5. **Continue to the next prompt** until all are done.
6. **When all prompts are done** — add a final "✅ All prompts completed" line to `_PROGRESS.md`.

### Why:
- `_PROGRESS.md` acts as a resumable checkpoint inside the prompt library itself.
- If stuck mid-way, reading `_PROGRESS.md` tells exactly where to continue.
- Deleting executed prompts keeps the directory clean — only pending prompts remain.
- `CLAUDE.md` stays focused on workflows only — no status data here.

## חשיבה תקועה — כלל עצירה (מחוזק)

### אם אתה מזהה אחד מהתסמינים הבאים בחשיבה שלך:
1. **לולאת ניסיונות** — ניסית 2+ גישות שונות לאותה בעיה וכולן נכשלו
2. **קריאת קבצים מוגזמת** — אתה שוקל לקרוא יותר מ-5 קבצים לאותו task
3. **ניתוח מתארך** — אתה כותב ניתוח של יותר מ-3 פסקאות
4. **מורכבות יתר** — עברו 15+ tool uses ואתה עדיין רחוק מפתרון

### מה לעשות:
- **עצור מיד** — אל תמשיך לחשוב / לנסות
- **כתוב למשתמש** סיכום ברור של: מה ניסית, מה נכשל, מה חסר, מה אתה צריך
- **הצע מסלולים אפשריים** — בקש עזרה, הצע לפרק את הבעיה, או הצע גישה חלופית
- **אל תנחש** — אל תמשיך עם פתרון שאתה לא בטוח בו

### למה זה חשוב:
- חשיבה ממושכת ללא פלט = בזבוז context window וזמן
- עדיף לעצור ולשאול מאשר להמשיך בכיוון שגוי
- המשתמש יכול לתת מידע שיחסוך דקות של ניחושים
