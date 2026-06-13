#!/usr/bin/env python3
"""Build the managers' review PDF from COMBINED_FOR_MANAGERS.md.

Pipeline: Markdown -> styled RTL HTML -> PDF (via LibreOffice headless).

The source Markdown uses ``@@PAGEBREAK@@`` on its own line as a hard page break.

Usage:
    python3 scripts/build_managers_pdf.py

Requires: python3-markdown (system) and libreoffice/soffice on PATH.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import markdown  # provided by the system python (python3-markdown)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "COMBINED_FOR_MANAGERS.md"
PDF_OUT = ROOT / "מערכת_ניהול_משמרות_סקירה_ותכנון.pdf"

PAGE_BREAK = "@@PAGEBREAK@@"

CSS = """
@page { size: A4; margin: 2.2cm 2cm; }
* { box-sizing: border-box; }
body {
  font-family: "Noto Sans Hebrew", "Noto Sans", "DejaVu Sans", sans-serif;
  direction: rtl;
  text-align: right;
  color: #2b2b2b;
  font-size: 12.5pt;
  line-height: 1.7;
}
h1 {
  color: #3b3b7a;
  font-size: 22pt;
  border-bottom: 2px solid #3b3b7a;
  padding-bottom: 8px;
  margin-top: 0;
}
h2 {
  color: #3b3b7a;
  font-size: 16pt;
  border-bottom: 1px solid #c9c9e0;
  padding-bottom: 5px;
  margin-top: 28px;
}
h3 { color: #4a4a8a; font-size: 13.5pt; margin-top: 18px; }
p, li { line-height: 1.7; }
strong { color: #1f1f4a; }
em { color: #555; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 14px 0;
  direction: rtl;
}
th {
  background: #3b3b7a;
  color: #ffffff;
  font-weight: bold;
  padding: 8px 10px;
  text-align: right;
  border: 1px solid #3b3b7a;
}
td {
  padding: 7px 10px;
  border: 1px solid #c9c9e0;
  text-align: right;
  vertical-align: top;
}
tr:nth-child(even) td { background: #f3f3fa; }
blockquote {
  background: #eef0fb;
  border-right: 4px solid #3b3b7a;
  border-left: none;
  margin: 14px 0;
  padding: 10px 16px;
  border-radius: 4px;
}
blockquote p { margin: 6px 0; }
hr { border: none; border-top: 2px solid #c9c9e0; margin: 18px 0; }
ul { padding-right: 22px; padding-left: 0; }
.pagebreak { page-break-before: always; }
"""

MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists", "attr_list", "nl2br"]


def build_html() -> str:
    text = SRC.read_text(encoding="utf-8")
    segments = text.split(PAGE_BREAK)
    html_parts = []
    for i, seg in enumerate(segments):
        if i > 0:
            html_parts.append('<div class="pagebreak"></div>')
        html_parts.append(
            markdown.markdown(seg.strip(), extensions=MD_EXTENSIONS)
        )
    body = "\n".join(html_parts)
    return (
        '<!DOCTYPE html>\n<html lang="he" dir="rtl">\n<head>\n'
        '<meta charset="utf-8">\n<style>' + CSS + "</style>\n</head>\n<body>\n"
        + body
        + "\n</body>\n</html>\n"
    )


def main() -> int:
    if not SRC.exists():
        print(f"missing source: {SRC}", file=sys.stderr)
        return 1
    html = build_html()
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        html_path = tmpdir / "doc.html"
        html_path.write_text(html, encoding="utf-8")
        # LibreOffice writes <stem>.pdf into the outdir.
        proc = subprocess.run(
            [
                "soffice", "--headless", "--convert-to", "pdf",
                "--outdir", str(tmpdir), str(html_path),
            ],
            capture_output=True, text=True, timeout=180,
        )
        if proc.returncode != 0:
            print(proc.stdout, proc.stderr, file=sys.stderr)
            return proc.returncode
        produced = tmpdir / "doc.pdf"
        if not produced.exists():
            print("soffice did not produce doc.pdf", proc.stdout, proc.stderr,
                  file=sys.stderr)
            return 1
        PDF_OUT.write_bytes(produced.read_bytes())
    print(f"wrote {PDF_OUT} ({PDF_OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
