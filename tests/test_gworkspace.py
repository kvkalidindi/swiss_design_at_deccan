"""Tests for the Google Workspace deliverables."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.lib import gmail_signature

ROOT = Path(__file__).resolve().parents[1]
SIG = ROOT / "gworkspace" / "gmail-signature.html"


@pytest.fixture(scope="module", autouse=True)
def regenerate():
    gmail_signature.emit_gmail_signature()


def test_signature_exists():
    assert SIG.exists()


def test_signature_under_gmail_limit():
    """Gmail enforces ~10 KB on signatures; we target well under."""
    size = SIG.stat().st_size
    assert size < 10_000, f"Signature is {size} bytes, over Gmail's 10 KB limit"


def test_signature_has_logo_data_url():
    text = SIG.read_text(encoding="utf-8")
    assert "data:image/png;base64," in text


def test_signature_has_brand_color():
    text = SIG.read_text(encoding="utf-8")
    assert "#164999" in text


def test_signature_has_ibm_plex():
    text = SIG.read_text(encoding="utf-8")
    assert "IBM Plex Sans" in text


def test_signature_has_company_domain():
    text = SIG.read_text(encoding="utf-8")
    assert "deccanchemicals.com" in text


def test_signature_idempotent():
    gmail_signature.emit_gmail_signature()
    text1 = SIG.read_text(encoding="utf-8")
    gmail_signature.emit_gmail_signature()
    text2 = SIG.read_text(encoding="utf-8")
    assert text1 == text2
