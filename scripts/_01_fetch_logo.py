"""Fetch deccanchemicals.com homepage and download the corporate logo."""
from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

WEBSITE = "https://deccanchemicals.com"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "logo.png"


def find_logo_url(html: str, base_url: str) -> str | None:
    """Locate logo URL in HTML by priority: header > alt-text > class."""
    soup = BeautifulSoup(html, "html.parser")

    # 1. Try <header> img
    header = soup.find("header")
    if header:
        img = header.find("img")
        if img and img.get("src"):
            return urljoin(base_url, img["src"])

    # 2. Try img with alt containing "deccan" (case-insensitive)
    for img in soup.find_all("img"):
        alt = (img.get("alt") or "").lower()
        if "deccan" in alt and img.get("src"):
            return urljoin(base_url, img["src"])

    # 3. Try img with src or class containing "logo"
    for img in soup.find_all("img"):
        src = (img.get("src") or "").lower()
        cls = " ".join(img.get("class") or []).lower()
        if "logo" in src or "logo" in cls:
            if img.get("src"):
                return urljoin(base_url, img["src"])

    return None


def main() -> int:
    """Fetch the website and download the logo."""
    resp = requests.get(WEBSITE, timeout=15, verify=False)
    resp.raise_for_status()

    url = find_logo_url(resp.text, WEBSITE)
    if not url:
        print(
            "ERROR: could not auto-locate logo. Save it manually to data/logo.png.",
            file=sys.stderr,
        )
        return 1

    print(f"Logo URL: {url}")

    img = requests.get(url, timeout=15, verify=False)
    img.raise_for_status()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(img.content)
    print(f"Saved to {OUT_PATH} ({len(img.content)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
