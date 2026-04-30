"""Emit skill/ from upstream .tmp_swiss/swiss-design/ + transformation map.

Reads:
- .tmp_swiss/swiss-design/SKILL.md and references/*.md
- data/skill-transformations.json

Writes:
- skill/SKILL.md, skill/references/{components,design-system,tailwind-config,prompting}.md
  (transformed copies of the upstream)
- skill/references/data-viz.md, skill/references/brand-marks.md (from inline templates)

Idempotent: running multiple times produces the same output.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TMP_SWISS = ROOT / ".tmp_swiss" / "swiss-design"
TRANSFORMS = ROOT / "data" / "skill-transformations.json"
SKILL = ROOT / "skill"

UPSTREAM_REFERENCES = ["components.md", "design-system.md", "tailwind-config.md", "prompting.md"]


def ensure_upstream() -> None:
    """Ensure .tmp_swiss/ is present; re-clone if missing."""
    if TMP_SWISS.exists():
        return
    target = ROOT / ".tmp_swiss"
    if target.exists():
        shutil.rmtree(target)
    subprocess.run(
        ["git", "clone", "https://github.com/zeke/swiss-design-skill", str(target)],
        check=True,
    )


def transform_text(text: str, transforms: dict) -> str:
    for sec in transforms.get("section_replacements", []):
        find = sec["find_block"]
        replace = sec["replace_block"]
        if find in text:
            text = text.replace(find, replace)
    for c in transforms.get("color_replacements", []):
        text = text.replace(c["find"], c["replace"])
    for n in transforms.get("name_replacements", []):
        text = text.replace(n["find"], n["replace"])
    return text


def rewrite_frontmatter(text: str, fm: dict) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("---", 3)
    if end == -1:
        return text
    new_fm_lines = [
        "---",
        f"name: {fm['name']}",
        f"description: {fm['description']}",
        f"license: {fm['license']}",
        "metadata:",
        f"  author: {fm['metadata']['author']}",
        f"  version: \"{fm['metadata']['version']}\"",
        f"  upstream: {fm['metadata']['upstream']}",
        f"  based_on: {fm['metadata']['based_on']}",
        "---",
    ]
    return "\n".join(new_fm_lines) + text[end + 3:]


def emit_data_viz_md() -> str:
    return """\
# Data Visualization — Deccan Palette

This document covers a deliberate exception to the **"one accent per project"** Swiss design rule (`design-system.md`). Charts and data visualizations follow different rules: they need multiple distinct colors to encode different series, and a single-color palette would be unreadable.

## When to use

This guidance applies ONLY to:
- Multi-series charts (line, bar, stacked area)
- Categorical encodings (heatmaps, treemaps, choropleths)
- Dashboards displaying numeric series

It does NOT apply to:
- UI chrome (buttons, links, navigation, surfaces)
- Single-value indicators (use the single Deccan Blue accent at appropriate opacity)
- Status indicators (use a separate traditional success/warning/error palette)

## The 8-step palette

Pulled from `outputs/palette.json` at the project root:

| Step | Hex | Role |
|------|-----|------|
| `blue-100`  | `#E0E8F5` | Background tint, fill |
| `blue-300`  | `#0EA3DD` | Bright cyan series, callout |
| `blue-500`  | `#164999` | Primary brand series, hero data |
| `blue-700`  | `#0C2956` | Dark emphasis series |
| `green-100` | `#E9EFE6` | Background tint, fill |
| `green-300` | `#A1CB8D` | Soft green series |
| `green-500` | `#71BF4D` | Secondary brand series |
| `green-700` | `#4F8D33` | Dark emphasis series |

## Recommended series order

For a 2-series chart: `blue-500`, `green-500`.
For a 4-series chart: `blue-500`, `green-500`, `blue-700`, `green-700`.
For an 8-series chart: cycle through all 8 in lightness order: `blue-500`, `green-500`, `blue-700`, `green-700`, `blue-300`, `green-300`, `blue-100`, `green-100`.

## Accessibility for charts

Color alone is never sufficient encoding for accessibility. Pair color with:
- Direct labels on series
- Distinct line styles (solid / dashed / dotted)
- Distinct marker shapes
- Pattern fills for grayscale-printed dashboards

Sources for the canonical palette: `outputs/palette.json` (machine-readable), `outputs/palette.css` (CSS variables), `outputs/palette.md` (documentation).
"""


def emit_brand_marks_md() -> str:
    return """\
# Brand Marks — Secondary Green Usage

The Deccan corporate logo includes a green leaf icon at `#71BF4D` (the `green-500` step in our palette). This document specifies its allowed usage in the design system.

## What is the secondary green mark?

`#71BF4D` is the dominant green from the Deccan logo. It appears alongside the deep blue navy (`#164999`) in the official mark.

## Where you may use the green mark

| Context | Allowed | Notes |
|---------|---------|-------|
| The corporate logo | Yes | The leaf icon is the canonical use. |
| Sustainability / ESG content | Yes | Hero illustrations, callouts, badges associated with explicit sustainability or environmental themes. |
| Charts / data visualization | Yes | See `references/data-viz.md`. Charts treat the palette differently. |
| Print collateral with sustainability theme | Yes | Annual sustainability reports, environmental certifications. |

## Where you may NOT use the green mark

The green is **never** to be used as a UI accent alongside or instead of Deccan Blue. The Swiss design "one accent" principle (`references/design-system.md`) governs all standard UI: buttons, links, navigation, active states, focus rings, hover indicators, structural accents.

| Context | Allowed | Reason |
|---------|---------|--------|
| Buttons, CTAs | NO | UI accents = Deccan Blue only. |
| Links, active nav | NO | UI accents = Deccan Blue only. |
| Borders, focus rings | NO | UI accents = Deccan Blue only. |
| Status indicators (success / warning / error) | NO | Use a separate traditional status palette, never the brand green. |
| Decorative elements not tied to sustainability | NO | The green has a specific meaning; using it decoratively dilutes that meaning. |

## Why this restriction matters

Mixing two accents undermines the visual hierarchy. Two equally-saturated brand colors fight for attention, and the user can no longer tell which color signals action. By restricting the green to logo and sustainability contexts, we preserve its meaning and keep the UI's call-to-action signal (Deccan Blue) unambiguous.

## Specifying it in code

When you DO use it (logo, sustainability):

```css
:root {
  --brand-green: #71BF4D;
  --brand-green-dark: #4F8D33;  /* green-700, for emphasis */
}
```

When in doubt: do not use it. Default to Deccan Blue.
"""


def main() -> int:
    ensure_upstream()
    transforms = json.loads(TRANSFORMS.read_text(encoding="utf-8"))

    if SKILL.exists():
        shutil.rmtree(SKILL)
    (SKILL / "references").mkdir(parents=True)

    skill_md = (TMP_SWISS / "SKILL.md").read_text(encoding="utf-8")
    skill_md = rewrite_frontmatter(skill_md, transforms["frontmatter"])
    skill_md = transform_text(skill_md, transforms)
    (SKILL / "SKILL.md").write_text(skill_md, encoding="utf-8")

    for ref in UPSTREAM_REFERENCES:
        src = (TMP_SWISS / "references" / ref).read_text(encoding="utf-8")
        out = transform_text(src, transforms)
        (SKILL / "references" / ref).write_text(out, encoding="utf-8")

    (SKILL / "references" / "data-viz.md").write_text(emit_data_viz_md(), encoding="utf-8")
    (SKILL / "references" / "brand-marks.md").write_text(emit_brand_marks_md(), encoding="utf-8")

    print("Generated:")
    for p in sorted(SKILL.rglob("*.md")):
        rel = p.relative_to(SKILL)
        size = p.stat().st_size
        print(f"  skill/{rel} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
