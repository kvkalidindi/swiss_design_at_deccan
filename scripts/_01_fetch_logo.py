"""Fetch deccanchemicals.com homepage and download the corporate logo.

Note: at the time of writing, deccanchemicals.com presented an SSL certificate
with a hostname mismatch and rejected requests lacking a browser User-Agent.
This script does the right thing (verifies TLS, sends a polite User-Agent) and
will report a clear error if the live site cannot be reached. If that happens,
manually save the logo to ``data/logo.png`` from a browser and re-run the
downstream pipeline; the rest of the pipeline only depends on that file.
"""
from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

WEBSITE = "https://deccanchemicals.com"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "logo.png"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def find_logo_url(html: str, base_url: str) -> str | None:
    """Locate logo URL in HTML by priority: header > alt-text > class."""
    soup = BeautifulSoup(html, "html.parser")

    header = soup.find("header")
    if header:
        img = header.find("img")
        if img and img.get("src"):
            return urljoin(base_url, img["src"])

    for img in soup.find_all("img"):
        alt = (img.get("alt") or "").lower()
        if "deccan" in alt and img.get("src"):
            return urljoin(base_url, img["src"])

    for img in soup.find_all("img"):
        src = (img.get("src") or "").lower()
        cls = " ".join(img.get("class") or []).lower()
        if "logo" in src or "logo" in cls:
            if img.get("src"):
                return urljoin(base_url, img["src"])

    return None


def main() -> int:
    try:
        resp = requests.get(WEBSITE, timeout=15, headers=HEADERS)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(
            f"ERROR fetching {WEBSITE}: {exc}\n"
            "Manual fallback: save the logo to data/logo.png from a browser and "
            "re-run the rest of the pipeline.",
            file=sys.stderr,
        )
        return 1

    url = find_logo_url(resp.text, WEBSITE)
    if not url:
        print(
            "ERROR: could not auto-locate logo. Save it manually to data/logo.png.",
            file=sys.stderr,
        )
        return 1

    print(f"Logo URL: {url}")

    try:
        img = requests.get(url, timeout=15, headers=HEADERS)
        img.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(
            f"ERROR fetching {url}: {exc}\n"
            "Manual fallback: save the logo to data/logo.png from a browser.",
            file=sys.stderr,
        )
        return 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(img.content)
    print(f"Saved to {OUT_PATH} ({len(img.content)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
