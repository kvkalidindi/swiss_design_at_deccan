"""Download IBM Plex + 5 fallback fonts from the google/fonts mirror.

Sources are TTFs in the google/fonts repository (raw.githubusercontent.com),
which is the most stable public source for these OFL'd font files. Each
download is validated for TTF magic bytes (00 01 00 00, OTTO, or 'true')
before being written; otherwise the file is rejected and the run fails.

Earlier revisions of this script saved the response of an HTML download form
into .ttf files, which Office and GlyphTypeface then refused to load. The
magic-byte check guards against that regression.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "typography" / "substitution-map.json"
OUT = ROOT / "fonts"

_GH = "https://raw.githubusercontent.com/google/fonts/main/ofl"

# family-slug -> [(filename, url)]
SOURCES: dict[str, list[tuple[str, str]]] = {
    "ibm-plex-sans": [
        ("IBMPlexSans-VariableFont.ttf",        f"{_GH}/ibmplexsans/IBMPlexSans%5Bwdth%2Cwght%5D.ttf"),
        ("IBMPlexSans-Italic-VariableFont.ttf", f"{_GH}/ibmplexsans/IBMPlexSans-Italic%5Bwdth%2Cwght%5D.ttf"),
    ],
    "ibm-plex-mono": [
        ("IBMPlexMono-Regular.ttf", f"{_GH}/ibmplexmono/IBMPlexMono-Regular.ttf"),
        ("IBMPlexMono-Bold.ttf",    f"{_GH}/ibmplexmono/IBMPlexMono-Bold.ttf"),
    ],
    "hanken-grotesk": [
        ("HankenGrotesk-VariableFont.ttf", f"{_GH}/hankengrotesk/HankenGrotesk%5Bwght%5D.ttf"),
    ],
    "barlow": [
        ("Barlow-Regular.ttf", f"{_GH}/barlow/Barlow-Regular.ttf"),
        ("Barlow-Bold.ttf",    f"{_GH}/barlow/Barlow-Bold.ttf"),
    ],
    "host-grotesk": [
        ("HostGrotesk-VariableFont.ttf", f"{_GH}/hostgrotesk/HostGrotesk%5Bwght%5D.ttf"),
    ],
    "dm-sans": [
        ("DMSans-VariableFont.ttf", f"{_GH}/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf"),
    ],
    "fira-code": [
        ("FiraCode-VariableFont.ttf", f"{_GH}/firacode/FiraCode%5Bwght%5D.ttf"),
    ],
}

# Family-slug -> license file URL.
LICENSE_URLS: dict[str, str] = {
    "ibm-plex-sans":  f"{_GH}/ibmplexsans/OFL.txt",
    "ibm-plex-mono":  f"{_GH}/ibmplexmono/OFL.txt",
    "hanken-grotesk": f"{_GH}/hankengrotesk/OFL.txt",
    "barlow":         f"{_GH}/barlow/OFL.txt",
    "host-grotesk":   f"{_GH}/hostgrotesk/OFL.txt",
    "dm-sans":        f"{_GH}/dmsans/OFL.txt",
    "fira-code":      f"{_GH}/firacode/OFL.txt",
}


def is_valid_ttf(data: bytes) -> bool:
    if len(data) < 4:
        return False
    head = data[:4]
    return head in (b"\x00\x01\x00\x00", b"OTTO", b"true")


def fetch_binary(url: str) -> bytes:
    r = requests.get(url, timeout=60, allow_redirects=True)
    r.raise_for_status()
    return r.content


def main() -> int:
    # The substitution map drives which families we package; the SOURCES table
    # provides the URLs. If a substitution-map family lacks a SOURCES entry,
    # warn and skip (rather than silently producing a placeholder).
    sub = json.loads(MAP.read_text(encoding="utf-8"))
    requested = {
        s["family"].lower().replace(" ", "-"): s["family"]
        for s in sub["canonical_stack"]
    }
    fail = 0
    for slug, family in requested.items():
        if slug not in SOURCES:
            print(f"WARN: no SOURCES entry for {family} ({slug}); skipping", file=sys.stderr)
            fail += 1
            continue
        dest = OUT / slug
        dest.mkdir(parents=True, exist_ok=True)
        # Fonts
        for filename, url in SOURCES[slug]:
            print(f"  -> {slug}/{filename}")
            try:
                data = fetch_binary(url)
                if not is_valid_ttf(data):
                    print(
                        f"    REJECTED: not a valid TTF (first 4 bytes: {data[:4]!r}, {len(data)} bytes total)",
                        file=sys.stderr,
                    )
                    fail += 1
                    continue
                (dest / filename).write_bytes(data)
                print(f"    OK ({len(data):,} bytes)")
            except Exception as exc:
                print(f"    FAILED: {exc}", file=sys.stderr)
                fail += 1
        # License
        if slug in LICENSE_URLS:
            license_path = dest / "OFL.txt"
            try:
                data = fetch_binary(LICENSE_URLS[slug])
                license_path.write_bytes(data)
                print(f"  -> {slug}/OFL.txt OK ({len(data):,} bytes)")
            except Exception as exc:
                print(f"  -> {slug}/OFL.txt FAILED: {exc}", file=sys.stderr)
                fail += 1
    print()
    print(f"Done. {len(requested)} families processed; {fail} failures.")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
