"""Render python_admin_guide.pdf from the v3 template + extracted body text.

Reads the body text from the previous (font-broken) PDF's text extraction,
parses it into headings + paragraphs, fills the v3 self-contained template,
and renders to PDF using headless Edge / Chrome on Windows. The output is
intended to verify the IBM Plex inlining fix end-to-end.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skill" / "assets" / "templates" / "document.html"
SRC_TXT = Path(r"C:\Users\kishore.kalidindi\Downloads\python_admin_guide_3.txt")
OUT_DIR = ROOT / "outputs"
OUT_HTML = OUT_DIR / "python_admin_guide.html"
OUT_PDF = OUT_DIR / "python_admin_guide.pdf"

EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

META = {
    "TITLE": "Python and Jupyter on the Deccan Network",
    "SUBTITLE": "An administrator's guide for engineering and IT workstations",
    "DOCUMENT_TYPE": "Standard",
    "PREPARED_BY": "Office of the SVP, IT &amp; Digital Transformation",
    "DATE": "May 2026",
    "VERSION": "1.0",
    "CLASSIFICATION": "Confidential",
}

# Lines that are recognized as H1 section headings. Pulled from the
# scanned/extracted layout of python_admin_guide_3.pdf; any line whose
# stripped text exactly equals one of these (case-insensitive) becomes <h1>.
H1_TITLES = {
    "purpose and scope",
    "python version selection",
    "distribution selection",
    "dependency management",
    "the package mirror",
    "the notebook layer",
    "vulnerability and provenance controls",
    "identity, secrets, and endpoint controls",
    "policy and lifecycle",
    "approved stack",
    "prohibited",
    "open questions for the next revision",
}

FOOTER_RE = re.compile(r"^\s*Deccan Fine Chemicals\s+.\s+Confidential\s+\d+\s*$")
COVER_LINES = 10  # title + subtitle + 5-row metadata block + blank lines


def _normalize(line: str) -> str:
    return line.replace(" ", " ").rstrip()


def _strip_furniture(lines: list[str]) -> list[str]:
    return [ln for ln in lines if not FOOTER_RE.match(ln)]


def _parse_body(text: str) -> str:
    raw = [_normalize(ln) for ln in text.splitlines()]
    raw = raw[COVER_LINES:]  # drop cover block
    raw = _strip_furniture(raw)

    # Collapse runs of blank lines into single separators.
    blocks: list[list[str]] = []
    cur: list[str] = []
    for ln in raw:
        if ln.strip() == "":
            if cur:
                blocks.append(cur)
                cur = []
        else:
            cur.append(ln)
    if cur:
        blocks.append(cur)

    # An H1 may span two lines in the extracted text (e.g. "Open questions for"
    # then "the next revision"). Re-join any 1-2 line block whose joined form
    # matches a known title.
    out_html: list[str] = []
    for block in blocks:
        joined = " ".join(s.strip() for s in block).strip()
        joined_lc = joined.lower()
        if len(block) <= 2 and joined_lc in H1_TITLES:
            out_html.append(f"    <h1>{_html_escape(joined)}</h1>")
            continue
        para = " ".join(s.strip() for s in block).strip()
        if not para:
            continue
        out_html.append(f"    <p>{_html_escape(para)}</p>")
    return "\n".join(out_html)


def _html_escape(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;"))


def _fill_template(template: str, body_html: str) -> str:
    rendered = template
    for key, value in META.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    rendered = rendered.replace("{{BODY_HTML}}", body_html)
    return rendered


def _render_pdf(html_path: Path, pdf_path: Path) -> None:
    binary = EDGE if EDGE.exists() else CHROME
    if not binary.exists():
        raise SystemExit(f"no Edge or Chrome at expected paths")
    file_url = "file:///" + str(html_path).replace("\\", "/")
    cmd = [
        str(binary),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        file_url,
    ]
    print("rendering:", " ".join(cmd))
    subprocess.run(cmd, check=True, timeout=120)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not TEMPLATE.exists():
        print(f"missing template: {TEMPLATE}", file=sys.stderr)
        return 1
    if not SRC_TXT.exists():
        print(f"missing source text: {SRC_TXT}", file=sys.stderr)
        return 1

    template = TEMPLATE.read_text(encoding="utf-8")
    src = SRC_TXT.read_text(encoding="utf-8", errors="replace")
    body_html = _parse_body(src)
    rendered = _fill_template(template, body_html)
    OUT_HTML.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUT_HTML} ({OUT_HTML.stat().st_size:,} bytes)")

    OUT_PDF.unlink(missing_ok=True)
    _render_pdf(OUT_HTML, OUT_PDF)
    print(f"wrote {OUT_PDF} ({OUT_PDF.stat().st_size:,} bytes)")

    # Copy alongside the historical guides so the user can compare side-by-side.
    downloads_copy = Path(r"C:\Users\kishore.kalidindi\Downloads\python_admin_guide_4.pdf")
    shutil.copy(OUT_PDF, downloads_copy)
    print(f"copied to {downloads_copy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
