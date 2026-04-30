"""Download chosen Google Fonts (TTF + OFL.txt) into fonts/<family>/."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "typography" / "substitution-map.json"
OUT = ROOT / "fonts"

# Fallback: Google Fonts API + GitHub mirrors
# Format: family -> [(filename, google_fonts_family_name, github_license_url)]
SOURCES = {
    "IBM Plex Sans": [
        ("IBMPlexSans-Regular.ttf", "IBM Plex Sans", "https://github.com/IBM/plex/raw/main/LICENSE.txt"),
        ("IBMPlexSans-Bold.ttf", "IBM Plex Sans", "https://github.com/IBM/plex/raw/main/LICENSE.txt"),
        ("OFL.txt", "IBM Plex Sans", "https://github.com/IBM/plex/raw/main/LICENSE.txt"),
    ],
    "IBM Plex Mono": [
        ("IBMPlexMono-Regular.ttf", "IBM Plex Mono", "https://github.com/IBM/plex/raw/main/LICENSE.txt"),
        ("IBMPlexMono-Bold.ttf", "IBM Plex Mono", "https://github.com/IBM/plex/raw/main/LICENSE.txt"),
        ("OFL.txt", "IBM Plex Mono", "https://github.com/IBM/plex/raw/main/LICENSE.txt"),
    ],
    "Hanken Grotesk": [
        ("HankenGrotesk-VariableFont.ttf", "Hanken Grotesk", "https://github.com/hanken-design/HankenGrotesk/raw/main/OFL.txt"),
        ("OFL.txt", "Hanken Grotesk", "https://github.com/hanken-design/HankenGrotesk/raw/main/OFL.txt"),
    ],
    "Barlow": [
        ("Barlow-Regular.ttf", "Barlow", "https://github.com/jpt/barlow/raw/master/OFL.txt"),
        ("Barlow-Bold.ttf", "Barlow", "https://github.com/jpt/barlow/raw/master/OFL.txt"),
        ("OFL.txt", "Barlow", "https://github.com/jpt/barlow/raw/master/OFL.txt"),
    ],
    "Host Grotesk": [
        ("HostGrotesk-VariableFont.ttf", "Host Grotesk", "https://github.com/lettersoup/Host-Grotesk/raw/main/OFL.txt"),
        ("OFL.txt", "Host Grotesk", "https://github.com/lettersoup/Host-Grotesk/raw/main/OFL.txt"),
    ],
    "DM Sans": [
        ("DMSans-VariableFont.ttf", "DM Sans", "https://github.com/googlefonts/dm-fonts/raw/master/Sans/OFL.txt"),
        ("OFL.txt", "DM Sans", "https://github.com/googlefonts/dm-fonts/raw/master/Sans/OFL.txt"),
    ],
    "Fira Code": [
        ("FiraCode-VariableFont.ttf", "Fira Code", "https://github.com/tonsky/FiraCode/raw/master/LICENSE"),
        ("OFL.txt", "Fira Code", "https://github.com/tonsky/FiraCode/raw/master/LICENSE"),
    ],
}


def _slug(family: str) -> str:
    return family.lower().replace(" ", "-")


def _fetch_from_google_fonts_api(family: str) -> bytes | None:
    """Try to fetch font from Google Fonts API."""
    try:
        url = f"https://fonts.google.com/download?family={quote(family)}"
        r = requests.get(url, timeout=60, allow_redirects=True)
        r.raise_for_status()
        return r.content
    except Exception as e:
        print(f"    Google Fonts API unavailable: {e}", file=sys.stderr)
        return None


def main() -> int:
    sub = json.loads(MAP.read_text(encoding="utf-8"))
    families = [s["family"] for s in sub["canonical_stack"]]
    overall_ok = True
    for fam in families:
        if fam not in SOURCES:
            print(f"WARN: no SOURCES entry for {fam}", file=sys.stderr)
            overall_ok = False
            continue
        dest = OUT / _slug(fam)
        dest.mkdir(parents=True, exist_ok=True)
        for filename, gf_family, license_url in SOURCES[fam]:
            print(f"  -> {fam}/{filename}")
            try:
                if filename == "OFL.txt":
                    # Try to fetch license file from GitHub
                    r = requests.get(license_url, timeout=60, allow_redirects=True)
                    r.raise_for_status()
                    (dest / filename).write_bytes(r.content)
                else:
                    # Try Google Fonts API
                    content = _fetch_from_google_fonts_api(gf_family)
                    if content:
                        (dest / filename).write_bytes(content)
                    else:
                        raise requests.exceptions.RequestException(
                            "Could not fetch from Google Fonts"
                        )
            except requests.exceptions.RequestException as exc:
                print(f"    FAILED ({exc})", file=sys.stderr)
                # Create placeholder with download instructions
                placeholder = (
                    f"# Font file placeholder: {filename}\n\n"
                    f"Family: {fam}\n"
                    f"Download from: https://fonts.google.com/specimen/{quote(fam.replace(' ', '+'))}\n\n"
                    f"To use this font:\n"
                    f"1. Visit the URL above\n"
                    f"2. Download the TTF files\n"
                    f"3. Place in this directory: {dest}\n\n"
                )
                (dest / filename).write_text(placeholder, encoding="utf-8")
                overall_ok = False
    print("Done." if overall_ok else "Done with placeholders (see above).")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
