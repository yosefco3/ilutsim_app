#!/usr/bin/env python3
"""
Test Graph Generator - Maps test files to source files and shows test status.

Usage:
    python scripts/test_graph.py          # Generate TEST_GRAPH.md
    python scripts/test_graph.py --run    # Also run tests and show pass/fail status

Output: TEST_GRAPH.md
"""

import ast
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
FRONTEND_DIR = REPO_ROOT / "frontend"

# ── Backend mapping ──────────────────────────────────────────

BACKEND_SOURCE_DIRS = [
    "app/models",
    "app/repositories",
    "app/services",
    "app/controllers",
    "app/schemas",
    "app/bot",
    "app/utils",
    "app",
]

BACKEND_TEST_DIR = "tests"

# Manual overrides: test_file -> [source_files]
# When auto-detection isn't enough
BACKEND_MANUAL_MAP = {
    "test_health.py": ["app/main.py"],
    "test_config.py": ["app/config.py"],
    "test_bot.py": ["app/bot/bot_router.py", "app/bot/core.py", "app/bot/notifications.py", "app/bot/cron.py"],
    "test_models.py": [
        "app/models/user.py", "app/models/admin.py", "app/models/schedule_event.py",
        "app/models/schedule_week.py", "app/models/weekly_submission.py",
        "app/models/daily_status.py", "app/models/shift_window.py", "app/models/system_setting.py",
    ],
    "test_repositories.py": [
        "app/repositories/user_repository.py", "app/repositories/admin_repository.py",
        "app/repositories/schedule_event_repository.py", "app/repositories/schedule_week_repository.py",
        "app/repositories/submission_repository.py", "app/repositories/system_settings_repository.py",
    ],
    "test_controllers.py": [
        "app/controllers/auth_controller.py", "app/controllers/submission_controller.py",
        "app/controllers/admin_users_controller.py", "app/controllers/admin_weeks_controller.py",
        "app/controllers/admin_events_controller.py", "app/controllers/admin_notifications_controller.py",
        "app/controllers/admin_export_controller.py",
    ],
    "test_schemas.py": [
        "app/schemas/user_schemas.py", "app/schemas/week_schemas.py",
        "app/schemas/submission_schemas.py", "app/schemas/event_schemas.py",
        "app/schemas/common_schemas.py",
    ],
    "test_export.py": ["app/services/excel_export_service.py", "app/controllers/admin_export_controller.py"],
    "test_date_utils.py": ["app/utils/date_utils.py"],
    "test_current_week.py": ["app/services/week_service.py", "app/repositories/schedule_week_repository.py"],
    "test_open_week.py": ["app/services/week_service.py", "app/controllers/admin_weeks_controller.py"],
    "test_status_transitions.py": ["app/services/week_service.py", "app/constants.py"],
    "test_week_workflow.py": ["app/services/week_service.py", "app/repositories/schedule_week_repository.py"],
    "test_initial_seed.py": ["app/seed.py"],
    "test_notification_on_open.py": ["app/bot/notifications.py", "app/services/week_service.py"],
    "test_submission_guard.py": ["app/controllers/submission_controller.py", "app/services/week_service.py"],
    "test_e2e.py": ["app/main.py"],
}

# ── Frontend mapping ─────────────────────────────────────────

FRONTEND_MANUAL_MAP = {
    # webapp
    "webapp/tests/apiClient.test.js": ["webapp/src/api/apiClient.js"],
    "webapp/tests/messages.test.js": ["webapp/src/utils/messages.js"],
    "webapp/tests/components.test.jsx": [
        "webapp/src/components/SubmissionForm.jsx",
        "webapp/src/components/DayRow.jsx",
        "webapp/src/components/LockBanner.jsx",
    ],
    # admin
    "admin/tests/apiClient.test.js": ["admin/src/api/adminApiClient.js"],
    "admin/tests/messages.test.js": ["admin/src/utils/messages.js"],
    "admin/tests/components.test.jsx": [
        "admin/src/components/EventForm.jsx",
        "admin/src/components/ProtectedRoute.jsx",
        "admin/src/components/StatusGrid.jsx",
        "admin/src/components/Navbar.jsx",
        "admin/src/components/WeekStatusControl.jsx",
        "admin/src/components/ConfirmDialog.jsx",
        "admin/src/components/GuardForm.jsx",
        "admin/src/components/GuardTable.jsx",
    ],
}


def get_all_source_files() -> list[str]:
    """Get all backend source .py files."""
    files = []
    for d in BACKEND_SOURCE_DIRS:
        full = BACKEND_DIR / d
        if full.is_file() and full.suffix == ".py" and full.name != "__init__.py":
            files.append(d + "/" + full.name if "/" not in d else str(full.relative_to(BACKEND_DIR)))
        elif full.is_dir():
            for f in full.rglob("*.py"):
                if f.name == "__init__.py":
                    continue
                rel = str(f.relative_to(BACKEND_DIR))
                files.append(rel)
    return sorted(set(files))


def get_all_test_files() -> list[str]:
    """Get all backend test .py files."""
    test_dir = BACKEND_DIR / BACKEND_TEST_DIR
    files = []
    for f in test_dir.glob("test_*.py"):
        files.append(f.name)
    return sorted(files)


def run_backend_tests() -> dict[str, str]:
    """Run pytest and collect per-test status."""
    results = {}
    try:
        cmd = [
            sys.executable, "-m", "pytest",
            "--tb=no", "-q", "--no-header",
            str(BACKEND_DIR / "tests"),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(BACKEND_DIR), timeout=120)
        output = proc.stdout + proc.stderr

        # Parse "FAILED tests/test_x.py::TestClass::test_name" or "PASSED ..."
        for line in output.splitlines():
            m = re.match(r"(PASSED|FAILED|ERROR)\s+(tests/)?(test_\w+\.py)", line.strip())
            if m:
                status, _, test_file = m.groups()
                results[test_file] = status
                continue
            # Also try the summary line format
            m = re.match(r"(FAILED|PASSED|ERROR)\s+(test_\w+\.py)", line.strip())
            if m:
                status, test_file = m.groups()
                results[test_file] = status

        # Try to get individual test results from verbose output
        cmd2 = [
            sys.executable, "-m", "pytest",
            "--tb=no", "-v", "--no-header",
            str(BACKEND_DIR / "tests"),
        ]
        proc2 = subprocess.run(cmd2, capture_output=True, text=True, cwd=str(BACKEND_DIR), timeout=120)
        for line in proc2.stdout.splitlines():
            m = re.match(r"(PASSED|FAILED|ERROR)\s+(tests/)?(test_\w+\.py)", line.strip())
            if m:
                status, _, test_file = m.groups()
                if test_file not in results:
                    results[test_file] = status
            m = re.match(r".*\b(PASSED|FAILED|ERROR)\b.*?(test_\w+\.py)", line)
            if m:
                status, test_file = m.groups()
                if test_file not in results:
                    results[test_file] = status

    except (subprocess.TimeoutExpired, Exception) as e:
        print(f"Warning: Could not run backend tests: {e}", file=sys.stderr)

    return results


def run_frontend_tests(subdir: str) -> dict[str, str]:
    """Run vitest in a frontend subdir and collect results."""
    results = {}
    pkg_dir = FRONTEND_DIR / subdir
    try:
        cmd = ["npx", "vitest", "run", "--reporter=verbose"]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(pkg_dir), timeout=120)
        output = proc.stdout + proc.stderr
        for line in output.splitlines():
            # Match: ✓ src/tests/messages.test.js (5 tests) or × src/tests/apiClient.test.js
            m = re.match(r"[✓✔×✗]\s+(.*?\.test\.\w+)", line)
            if m:
                test_file = m.group(1).strip()
                results[test_file] = "PASS" if line.strip().startswith(("✓", "✔")) else "FAIL"
            # Match vitest verbose: PASS tests/messages.test.js
            m = re.match(r"(PASS|FAIL)\s+(.*?\.test\.\w+)", line)
            if m:
                results[m.group(2)] = m.group(1)
    except (subprocess.TimeoutExpired, Exception) as e:
        print(f"Warning: Could not run {subdir} tests: {e}", file=sys.stderr)
    return results


def build_source_test_map() -> dict[str, list[str]]:
    """Map source_file -> [test_files]."""
    mapping = defaultdict(list)
    for test_file, source_files in BACKEND_MANUAL_MAP.items():
        for src in source_files:
            mapping[src].append(test_file)
    return dict(mapping)


def generate_markdown(
    source_test_map: dict[str, list[str]],
    backend_results: dict[str, str],
    frontend_results: dict[str, str],
    run_tests: bool,
) -> str:
    """Generate the TEST_GRAPH.md content."""
    lines = []
    lines.append("# Test Coverage Graph")
    lines.append("")
    lines.append(f"_נוצר אוטומטית ב: {datetime.now().strftime('%Y-%m-%d %H:%M')}_")
    lines.append("")

    # Stats
    all_source_files = get_all_source_files()
    covered = [s for s in all_source_files if s in source_test_map]
    uncovered = [s for s in all_source_files if s not in source_test_map]

    lines.append("## סיכום")
    lines.append("")
    lines.append(f"| מדד | ערך |")
    lines.append(f"|---|---|")
    lines.append(f"| קבצי קוד backend | {len(all_source_files)} |")
    lines.append(f"| קבצי קוד מכוסים בטסטים | {len(covered)} |")
    lines.append(f"| קבצי קוד ללא טסטים | {len(uncovered)} |")
    lines.append(f"| אחוז כיסוי | {len(covered) * 100 // max(len(all_source_files), 1)}% |")

    if run_tests and backend_results:
        passed = sum(1 for v in backend_results.values() if v == "PASSED" or v == "PASS")
        failed = sum(1 for v in backend_results.values() if v in ("FAILED", "FAIL", "ERROR"))
        lines.append(f"| טסטים עוברים (backend) | {passed} ✅ |")
        lines.append(f"| טסטים נכשלים (backend) | {failed} ❌ |")
    lines.append("")

    # Backend: Source → Tests mapping
    lines.append("## Backend: מיפוי קוד → טסטים")
    lines.append("")
    lines.append("| קובץ קוד | קובץ טסט | סטטוס |")
    lines.append("|---|---|---|")

    for src in sorted(source_test_map.keys()):
        test_files = source_test_map[src]
        for tf in sorted(test_files):
            if run_tests:
                status = backend_results.get(tf, "⚠️ NOT RUN")
                if status in ("PASSED", "PASS"):
                    icon = "🟢 PASS"
                elif status in ("FAILED", "FAIL"):
                    icon = "🔴 FAIL"
                elif status == "ERROR":
                    icon = "🔴 ERROR"
                else:
                    icon = "⚪ " + status
            else:
                icon = "—"
            # Shorten paths for readability
            src_short = src.replace("app/", "")
            lines.append(f"| `{src_short}` | `{tf}` | {icon} |")

    lines.append("")

    # Uncovered files
    if uncovered:
        lines.append("## Backend: קבצים ללא טסטים ⚪")
        lines.append("")
        lines.append("| קובץ קוד | תיקייה |")
        lines.append("|---|---|")
        for src in uncovered:
            parts = src.split("/")
            folder = "/".join(parts[:-1]) if len(parts) > 1 else "/"
            name = parts[-1]
            lines.append(f"| `{name}` | `{folder}` |")
        lines.append("")

    # Frontend
    lines.append("## Frontend: מיפוי טסטים")
    lines.append("")
    lines.append("| תת-פרויקט | קובץ קוד | קובץ טסט | סטטוס |")
    lines.append("|---|---|---|---|")

    for test_path, src_files in sorted(FRONTEND_MANUAL_MAP.items()):
        parts = test_path.split("/")
        subproject = parts[0]  # webapp / admin
        test_file = "/".join(parts[1:])
        for src in src_files:
            src_short = src.split("/", 1)[1] if "/" in src else src
            if run_tests:
                # Check frontend results
                status = "—"
                for ft_key, ft_status in frontend_results.items():
                    if test_file in ft_key or ft_key.endswith(test_file.split("/")[-1]):
                        status = "🟢 PASS" if ft_status in ("PASS", "PASSED") else "🔴 FAIL"
                        break
            else:
                status = "—"
            lines.append(f"| {subproject} | `{src_short}` | `{test_file}` | {status} |")
    lines.append("")

    # Test files detail
    lines.append("## Backend: רשימת קבצי טסט")
    lines.append("")
    all_tests = get_all_test_files()
    lines.append("| קובץ טסט | מכסה קבצי קוד | סטטוס |")
    lines.append("|---|---|---|")
    for tf in all_tests:
        srcs = BACKEND_MANUAL_MAP.get(tf, ["(auto-detect)"])
        src_count = len(srcs)
        if run_tests:
            status = backend_results.get(tf, "⚪ NOT RUN")
            if "PASS" in status:
                icon = "🟢"
            elif "FAIL" in status or "ERROR" in status:
                icon = "🔴"
            else:
                icon = "⚪"
        else:
            icon = "—"
        lines.append(f"| `{tf}` | {src_count} | {icon} |")
    lines.append("")

    return "\n".join(lines)


def main():
    run_tests = "--run" in sys.argv
    source_test_map = build_source_test_map()

    backend_results = {}
    frontend_results = {}

    if run_tests:
        print("Running backend tests...")
        backend_results = run_backend_tests()
        print(f"  Got {len(backend_results)} results")

        print("Running frontend webapp tests...")
        webapp_results = run_frontend_tests("webapp")
        for k, v in webapp_results.items():
            frontend_results[f"webapp/{k}"] = v

        print("Running frontend admin tests...")
        admin_results = run_frontend_tests("admin")
        for k, v in admin_results.items():
            frontend_results[f"admin/{k}"] = v

    md = generate_markdown(source_test_map, backend_results, frontend_results, run_tests)
    output_path = REPO_ROOT / "TEST_GRAPH.md"
    output_path.write_text(md, encoding="utf-8")
    print(f"\n✅ Generated: {output_path}")
    if run_tests:
        print(f"   Backend: {len(backend_results)} test results")
        print(f"   Frontend: {len(frontend_results)} test results")
    else:
        print("   Tip: Run with --run to include test pass/fail status")


if __name__ == "__main__":
    main()