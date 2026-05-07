"""Verify a rendered Deccan PDF actually embeds IBM Plex.

The earlier failure mode (python_admin_guide_3.pdf, 2026-05-07) was that the
rendering environment silently substituted DejaVu Sans for IBM Plex Sans
because Google Fonts egress was blocked and the relative @font-face URLs
didn't resolve. The PDF still rendered — it just didn't conform to the spec.
This script catches that class of failure by inspecting the embedded font
dictionary.

Usage:
    python -m scripts.verify_pdf_fonts <path/to/file.pdf> [...]

Exits 0 if every PDF embeds IBM Plex Sans + Mono and contains no DejaVu /
generic system-fallback families. Exits non-zero with a per-file report
otherwise.
"""
from __future__ import annotations

import re
import sys
import zlib
from pathlib import Path

REQUIRED = ("IBMPlexSans", "IBMPlexMono")
FORBIDDEN = ("DejaVuSans", "DejaVuSerif", "Liberation", "Nimbus", "FreeSans", "FreeMono")


def _pdf_text_pool(data: bytes) -> bytes:
    """Return the raw bytes plus inflated content of every FlateDecode stream.

    Font names live in the cross-reference (uncompressed) and in /BaseFont
    entries inside compressed object streams. Concatenating both gives a
    superset that's safe to substring-search.
    """
    pool = bytearray(data)
    for m in re.finditer(rb"stream[\r\n]+(.*?)endstream", data, flags=re.DOTALL):
        chunk = m.group(1).strip(b"\r\n")
        try:
            pool.extend(zlib.decompress(chunk))
        except zlib.error:
            pass
    return bytes(pool)


def verify(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing: {path}"]
    pool = _pdf_text_pool(path.read_bytes())
    problems: list[str] = []
    for needle in REQUIRED:
        if needle.encode("ascii") not in pool:
            problems.append(f"missing required font family: {needle}")
    for needle in FORBIDDEN:
        if needle.encode("ascii") in pool:
            problems.append(f"forbidden fallback family present: {needle}")
    return problems


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: verify_pdf_fonts.py <pdf> [<pdf> ...]", file=sys.stderr)
        return 2
    rc = 0
    for arg in argv:
        path = Path(arg)
        problems = verify(path)
        if problems:
            rc = 1
            print(f"FAIL {path}")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"OK   {path}  (IBMPlexSans + IBMPlexMono embedded, no fallbacks)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
