"""Tests for scripts/_08_emit_skill.py - the upstream-to-deccan skill emitter."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts import _08_emit_skill as emit


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill"
EXPECTED_FILES = [
    "SKILL.md",
    "references/components.md",
    "references/design-system.md",
    "references/tailwind-config.md",
    "references/prompting.md",
    "references/data-viz.md",
    "references/brand-marks.md",
]


@pytest.fixture(scope="module", autouse=True)
def regenerate_skill():
    """Regenerate skill/ before running validations."""
    emit.main()


def test_all_expected_files_exist():
    for rel in EXPECTED_FILES:
        assert (SKILL / rel).exists(), f"Missing {rel}"


def test_skill_md_has_deccan_frontmatter():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "name: swiss-design-deccan" in text
    assert "kvkalidindi" in text
    assert "version: \"0.2.0\"" in text
    assert "upstream: https://github.com/zeke/swiss-design-skill" in text


def test_no_upstream_accent_colors_remain():
    """Any reference to Swiss Red, Cobalt, Golden, or Forest hex codes is a bug."""
    forbidden_hex = ["#C8102E", "#003B8E", "#F0B429", "#2D6A4F"]
    for rel in EXPECTED_FILES:
        text = (SKILL / rel).read_text(encoding="utf-8")
        for hex_code in forbidden_hex:
            assert hex_code not in text, f"{rel} still contains {hex_code}"


def test_deccan_accent_present_in_design_files():
    for rel in ["SKILL.md", "references/design-system.md", "references/tailwind-config.md"]:
        text = (SKILL / rel).read_text(encoding="utf-8")
        assert "#164999" in text, f"{rel} missing Deccan Blue #164999"


def test_brand_marks_documents_secondary_green():
    text = (SKILL / "references/brand-marks.md").read_text(encoding="utf-8")
    assert "#71BF4D" in text
    assert "logo" in text.lower()
    assert "sustainability" in text.lower()
    assert "never" in text.lower() or "do not" in text.lower()


def test_data_viz_documents_full_palette():
    text = (SKILL / "references/data-viz.md").read_text(encoding="utf-8")
    for hex_code in ["#E0E8F5", "#0EA3DD", "#164999", "#0C2956",
                     "#E9EFE6", "#A1CB8D", "#71BF4D", "#4F8D33"]:
        assert hex_code in text, f"data-viz.md missing {hex_code}"


def test_emitter_is_idempotent():
    """Running the emitter twice produces identical output."""
    text1 = {rel: (SKILL / rel).read_text(encoding="utf-8") for rel in EXPECTED_FILES}
    emit.main()
    text2 = {rel: (SKILL / rel).read_text(encoding="utf-8") for rel in EXPECTED_FILES}
    assert text1 == text2


def test_no_leftover_upstream_swiss_names():
    for rel in EXPECTED_FILES:
        text = (SKILL / rel).read_text(encoding="utf-8")
        assert "Swiss Red" not in text, f"{rel} still mentions 'Swiss Red'"
