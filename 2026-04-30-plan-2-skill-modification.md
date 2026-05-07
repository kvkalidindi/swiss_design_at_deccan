# Plan 2: Deccan Swiss-Design Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce `skill/` — a Deccan-customized fork of [zeke/swiss-design-skill](https://github.com/zeke/swiss-design-skill) — that any user can install (copy to `~/.claude/skills/`) and have AI agents produce Deccan-branded UIs by default.

**Architecture:** A small Python emitter (`scripts/_08_emit_skill.py`) reads the upstream skill content from `.tmp_swiss/swiss-design/`, applies a declarative transformation map (color hex replacements + frontmatter rewrites), writes the result to `skill/`, and emits two new reference files (`data-viz.md`, `brand-marks.md`) from inline templates. Tests verify the output is correctly transformed. Single accent (`#164999`); secondary green mark (`#71BF4D`) is documented but excluded from default UI styling.

**Tech Stack:** Python 3.11+, pytest, no new runtime dependencies. Operates only on text files.

---

## File Structure

Project root: `C:\Users\kishore.kalidindi\CC\swiss_design_at_deccan\`

```
.
├── 2026-04-30-plan-2-skill-modification-design.md   # spec (existing)
├── 2026-04-30-plan-2-skill-modification.md          # this plan
├── data/
│   └── skill-transformations.json                   # NEW (Task 1) - declarative map
├── scripts/
│   └── _08_emit_skill.py                            # NEW (Task 3) - emitter
├── skill/                                           # NEW (Task 4) - generated output
│   ├── SKILL.md
│   └── references/
│       ├── components.md
│       ├── design-system.md
│       ├── tailwind-config.md
│       ├── prompting.md
│       ├── data-viz.md                              # generated from inline template
│       └── brand-marks.md                           # generated from inline template
└── tests/
    └── test_skill_emitter.py                        # NEW (Task 3) - TDD validation
```

The `.tmp_swiss/` clone (gitignored) is the source template. It already exists from Plan 1's audit task. If missing, the emitter re-clones it.

---

## Phase 1: Audit & Transformation Map

### Task 1: Audit upstream content and build transformation map

**Files:**
- Create: `data/skill-transformations.json`
- Read-only: `.tmp_swiss/swiss-design/SKILL.md`, `.tmp_swiss/swiss-design/references/*.md`

- [ ] **Step 1: Confirm `.tmp_swiss/` is present, re-clone if missing**

```powershell
Set-Location "C:\Users\kishore.kalidindi\CC\swiss_design_at_deccan"
if (-not (Test-Path ".tmp_swiss\swiss-design\SKILL.md")) {
    if (Test-Path ".tmp_swiss") { Remove-Item .tmp_swiss -Recurse -Force }
    git clone https://github.com/zeke/swiss-design-skill .tmp_swiss
}
Get-ChildItem .tmp_swiss\swiss-design -Recurse -File | Select-Object FullName
```

Expected: 5 files (SKILL.md + 4 reference markdowns).

- [ ] **Step 2: Search every accent color reference**

```powershell
Set-Location "C:\Users\kishore.kalidindi\CC\swiss_design_at_deccan\.tmp_swiss\swiss-design"
$pattern = '(?i)#C8102E|#003B8E|#F0B429|#2D6A4F|rgba\(200,\s*16,\s*46|rgba\(0,\s*59,\s*142|rgba\(240,\s*180,\s*41|rgba\(45,\s*106,\s*79|Swiss Red|Cobalt|Golden|Forest|swiss-design'
Get-ChildItem -Recurse -File -Include *.md |
    Select-String -Pattern $pattern |
    ForEach-Object { "$($_.RelativePath):$($_.LineNumber): $($_.Line.Trim())" }
```

Capture the output mentally — this is the raw inventory of what needs to change. Most lines will be in `tailwind-config.md` and `design-system.md`.

- [ ] **Step 3: Write `data/skill-transformations.json`**

This is a declarative map of every textual transformation. The emitter applies them in order.

```json
{
  "frontmatter": {
    "name": "swiss-design-deccan",
    "description": "Apply the Deccan Fine Chemicals design system (Swiss International Style adapted for Deccan brand). Use when styling Deccan webpages, cleaning up Deccan UIs, or applying the corporate design system. Single accent #164999 (deep navy), IBM Plex Sans typography, opacity-based hierarchy, structured grid. Secondary green mark #71BF4D is reserved for the corporate logo and explicit sustainability content only.",
    "license": "MIT",
    "metadata": {
      "author": "kvkalidindi",
      "version": "0.2.0",
      "upstream": "https://github.com/zeke/swiss-design-skill",
      "based_on": "swiss-design 1.0"
    }
  },
  "color_replacements": [
    { "find": "#C8102E", "replace": "#164999", "context": "primary accent (Swiss Red -> Deccan Blue)" },
    { "find": "rgba(200, 16, 46,", "replace": "rgba(22, 73, 153,", "context": "Swiss Red rgba -> Deccan Blue rgba" },
    { "find": "rgba(200,16,46,", "replace": "rgba(22,73,153,", "context": "no-space variant" }
  ],
  "name_replacements": [
    { "find": "Swiss Red", "replace": "Deccan Blue", "context": "primary accent name" }
  ],
  "section_replacements": [
    {
      "anchor": "### Choosing an accent",
      "context": "design-system.md table replacement",
      "find_block": "| Name | Hex | When to use |\n| ---- | --- | ----------- |\n| Swiss Red | `#C8102E` | Default. Bold, assertive. Good for CTAs, error states, structural accents. |\n| Cobalt | `#003B8E` | Corporate, technical, trustworthy. Good for data products, enterprise. |\n| Golden | `#F0B429` | Warm, editorial. Good for cultural, food, arts projects. |\n| Forest | `#2D6A4F` | Natural, calm. Good for health, sustainability, outdoor. |",
      "replace_block": "| Name | Hex | When to use |\n| ---- | --- | ----------- |\n| Deccan Blue | `#164999` | The single Deccan accent. Used for CTAs, links, buttons, active states, structural accents — at multiple opacities (60%/20%/10%) for hierarchy. |\n\n**Note:** Deccan also has a secondary green mark (`#71BF4D`) reserved for the corporate logo and explicit sustainability/environmental content. Never use it as a UI accent in concert with Deccan Blue. See `references/brand-marks.md` for guidance."
    },
    {
      "anchor": "/* Switching accent colors\n:root { --accent: #003B8E; }  Cobalt\n:root { --accent: #F0B429; }  Golden\n:root { --accent: #2D6A4F; }  Forest\n*/",
      "context": "tailwind-config.md - remove the multi-accent comment block",
      "find_block": "/* Switching accent colors */\n/* \n:root { --accent: #003B8E; }  Cobalt\n:root { --accent: #F0B429; }  Golden\n:root { --accent: #2D6A4F; }  Forest\n*/",
      "replace_block": "/* Deccan accent is fixed at #164999. Do NOT swap it for another color.\n   For chart/data-viz use, refer to references/data-viz.md (uses the full\n   8-step palette from outputs/palette.json). */"
    }
  ]
}
```

- [ ] **Step 4: Validate JSON**

```powershell
Set-Location "C:\Users\kishore.kalidindi\CC\swiss_design_at_deccan"
.\.venv\Scripts\python.exe -c "import json; json.load(open('data/skill-transformations.json')); print('OK')"
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```powershell
git add data/skill-transformations.json
git commit -m "feat(skill): declarative transformation map for upstream -> deccan"
```

---

## Phase 2: Emitter implementation

### Task 2: Write tests for the skill emitter

**Files:**
- Create: `tests/test_skill_emitter.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_skill_emitter.py`:

```python
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
    # Must explicitly forbid using green as UI accent in concert with blue
    assert "never" in text.lower() or "do not" in text.lower()


def test_data_viz_documents_full_palette():
    text = (SKILL / "references/data-viz.md").read_text(encoding="utf-8")
    # All 8 palette steps should be referenced
    for hex_code in ["#E0E8F5", "#0EA3DD", "#164999", "#0C2956",
                     "#E9EFE6", "#A1CB8D", "#71BF4D", "#4F8D33"]:
        assert hex_code in text, f"data-viz.md missing {hex_code}"


def test_emitter_is_idempotent(tmp_path):
    """Running the emitter twice produces identical output."""
    text1 = {rel: (SKILL / rel).read_text(encoding="utf-8") for rel in EXPECTED_FILES}
    emit.main()
    text2 = {rel: (SKILL / rel).read_text(encoding="utf-8") for rel in EXPECTED_FILES}
    assert text1 == text2


def test_no_leftover_upstream_swiss_names():
    """Should not say 'Swiss Red' anywhere - it's now Deccan Blue."""
    for rel in EXPECTED_FILES:
        text = (SKILL / rel).read_text(encoding="utf-8")
        assert "Swiss Red" not in text, f"{rel} still mentions 'Swiss Red'"
```

- [ ] **Step 2: Run, expect ImportError (emitter doesn't exist yet)**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_skill_emitter.py -v
```

Expected: ImportError on `scripts._08_emit_skill`.

- [ ] **Step 3: Commit (test-only, will fail until Task 3)**

```powershell
git add tests/test_skill_emitter.py
git commit -m "test(skill): TDD tests for skill emitter (failing pending Task 3)"
```

---

### Task 3: Implement `scripts/_08_emit_skill.py`

**Files:**
- Create: `scripts/_08_emit_skill.py`

- [ ] **Step 1: Implement the emitter**

Create `scripts/_08_emit_skill.py`:

```python
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
import re
import shutil
import subprocess
import sys
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
    """Apply color, name, and section replacements to text."""
    # Section replacements first (largest scope, must match upstream verbatim)
    for sec in transforms.get("section_replacements", []):
        find = sec["find_block"]
        replace = sec["replace_block"]
        if find in text:
            text = text.replace(find, replace)
    # Color hex replacements
    for c in transforms.get("color_replacements", []):
        text = text.replace(c["find"], c["replace"])
    # Name replacements
    for n in transforms.get("name_replacements", []):
        text = text.replace(n["find"], n["replace"])
    return text


def rewrite_frontmatter(text: str, fm: dict) -> str:
    """Replace the YAML frontmatter at the top of SKILL.md with our values."""
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
    """Inline template for the new data-viz.md reference."""
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
    """Inline template for the new brand-marks.md reference."""
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

    # Clean and recreate skill/
    if SKILL.exists():
        shutil.rmtree(SKILL)
    (SKILL / "references").mkdir(parents=True)

    # SKILL.md (frontmatter + body transformed)
    skill_md = (TMP_SWISS / "SKILL.md").read_text(encoding="utf-8")
    skill_md = rewrite_frontmatter(skill_md, transforms["frontmatter"])
    skill_md = transform_text(skill_md, transforms)
    (SKILL / "SKILL.md").write_text(skill_md, encoding="utf-8")

    # Reference markdowns (body transformed only)
    for ref in UPSTREAM_REFERENCES:
        src = (TMP_SWISS / "references" / ref).read_text(encoding="utf-8")
        out = transform_text(src, transforms)
        (SKILL / "references" / ref).write_text(out, encoding="utf-8")

    # New reference files (from templates)
    (SKILL / "references" / "data-viz.md").write_text(emit_data_viz_md(), encoding="utf-8")
    (SKILL / "references" / "brand-marks.md").write_text(emit_brand_marks_md(), encoding="utf-8")

    # Sanity check
    print("Generated:")
    for p in sorted(SKILL.rglob("*.md")):
        rel = p.relative_to(SKILL)
        size = p.stat().st_size
        print(f"  skill/{rel} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run the emitter**

```powershell
Set-Location "C:\Users\kishore.kalidindi\CC\swiss_design_at_deccan"
.\.venv\Scripts\python.exe scripts\_08_emit_skill.py
```

Expected: prints 7 generated files (`skill/SKILL.md` + 4 transformed references + 2 new ones).

- [ ] **Step 3: Run the test suite, expect PASS**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_skill_emitter.py -v
```

Expected: 8 tests pass.

If any test fails (e.g., a forbidden-color check finds an upstream hex that survived), inspect the upstream content and add the missing entry to `data/skill-transformations.json`. Re-run the emitter and tests.

- [ ] **Step 4: Manually inspect the generated SKILL.md**

```powershell
Get-Content skill\SKILL.md | Select-Object -First 30
```

Expected: top of file shows the new YAML frontmatter (`name: swiss-design-deccan`, etc.) followed by the body content with `#164999` substituted for `#C8102E`.

- [ ] **Step 5: Commit script + generated skill/**

```powershell
git add scripts/_08_emit_skill.py skill/
git status
git commit -m @'
feat(skill): emit Deccan-customized swiss-design skill

- scripts/_08_emit_skill.py reads upstream .tmp_swiss/ and applies the
  transformation map from data/skill-transformations.json
- skill/ now contains 7 files: SKILL.md, 4 transformed references, plus
  data-viz.md and brand-marks.md generated from inline templates
- All upstream accent colors (Swiss Red / Cobalt / Golden / Forest)
  replaced with single Deccan accent #164999
- Secondary green mark #71BF4D documented with explicit usage restrictions
- Idempotent: re-running produces identical output
'@
```

---

## Phase 3: Documentation & Release

### Task 4: Update README and document the install procedure

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read current README**

```powershell
Get-Content README.md
```

- [ ] **Step 2: Update Status section to reflect Plan 2 completion**

Add immediately under the existing "Plan 1 complete" status section, a new sub-section:

```markdown
**Plan 2 complete (v0.2.0)** — Deccan Swiss-design skill shipped.

- `skill/SKILL.md` + 6 reference files — installable Claude Code skill
- Single accent (`#164999`); secondary green mark restricted to logo / sustainability
- Re-generated from upstream via `scripts/_08_emit_skill.py` (idempotent)

### Installing the skill

**User-level install (recommended):**

```powershell
# Windows PowerShell
$dest = "$env:USERPROFILE\.claude\skills\swiss-design-deccan"
Copy-Item -Path skill -Destination $dest -Recurse -Force
```

```bash
# macOS / Linux
cp -r skill "$HOME/.claude/skills/swiss-design-deccan"
```

Claude Code picks it up automatically on next session.

**Plugin manifest install:** add an entry to `~/.claude/plugins/manifest.json`:

```json
{ "plugins": [
  { "name": "swiss-design-deccan", "path": "/absolute/path/to/swiss_design_at_deccan/skill" }
]}
```
```

Update the existing Roadmap section so Plan 2 is marked complete:

```markdown
## Roadmap

- ~~**Plan 2** — modify `zeke/swiss-design-skill` to consume these tokens~~ **complete (v0.2.0)**
- **Plan 3** — Microsoft Office artifacts (.thmx themes, .dotx/.potx/.xltx templates)
- **Plan 4** — Google Workspace artifacts (Slides/Docs templates, admin gallery)
- **Plan 5** — Enterprise deployment (Intune profiles, Group Policy, font installation)
```

- [ ] **Step 3: Commit**

```powershell
git add README.md
git diff --staged
git commit -m "docs: mark Plan 2 (deccan swiss-design skill) complete"
```

---

### Task 5: Tag v0.2.0 and push

- [ ] **Step 1: Tag**

```powershell
git tag -a v0.2.0 -m @'
Plan 2 release: Deccan swiss-design skill

- Customized Claude Code skill at skill/ - install to ~/.claude/skills/swiss-design-deccan/
- Single accent #164999 (Deccan Blue) replaces upstream Swiss Red and the 4-option accent table
- Secondary green mark #71BF4D documented and restricted to logo / sustainability contexts
- New references: data-viz.md (8-step palette for charts), brand-marks.md (green mark policy)
- Emitter scripts/_08_emit_skill.py is idempotent and re-runnable when palette evolves

Built on Plan 1 (v0.1.0) tokens.
Next: Plan 3 (Microsoft Office artifacts).
'@
```

- [ ] **Step 2: Push commits + tag to GitHub**

```powershell
git push origin main --tags
```

- [ ] **Step 3: Verify the tag is visible on the remote**

```powershell
git ls-remote --tags origin | Select-String v0.2.0
```

Expected: a line showing `refs/tags/v0.2.0`.

---

## Phase 4: Smoke test the install (manual)

### Task 6: End-to-end manual smoke test of the installable skill

This is a manual sanity check that the produced `skill/` is loadable by Claude Code.

- [ ] **Step 1: Copy to user skills dir**

```powershell
$dest = "$env:USERPROFILE\.claude\skills\swiss-design-deccan"
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Copy-Item -Path skill -Destination $dest -Recurse -Force
Get-ChildItem $dest -Recurse -File | Select-Object FullName
```

Expected: 7 files copied to the user skills directory.

- [ ] **Step 2: Verify Claude Code recognizes the skill**

In a NEW Claude Code session (any directory), run a quick test:

> "What skills are available related to design?"

Expected: the response should mention `swiss-design-deccan` with the description from the frontmatter.

If the skill doesn't appear, check the directory structure (must be `<skills>/swiss-design-deccan/SKILL.md` directly, not nested deeper).

- [ ] **Step 3: Smoke test agent invocation**

> "Using the swiss-design-deccan skill, sketch the styles for a hero section with a primary CTA button."

Expected: the agent should produce code using `#164999` as the accent, IBM Plex Sans typography, and stone neutral surfaces. It should NOT use the green mark in the UI.

- [ ] **Step 4: Document smoke test result**

If everything works, no action needed — Plan 2 is fully shipped.

If something breaks (skill not discovered, wrong colors used, etc.), open a follow-up issue or schedule a fix.

---

## Self-Review

**Spec coverage:**
- Spec §2 "philosophical alignment, single accent": Task 1 transformation map + Task 3 emitter
- Spec §3 "repo structure (`skill/` inside repo)": Task 3 emitter writes to `skill/`
- Spec §4 "file-by-file changes": Task 1 transformation map + Task 3 emitter execution
- Spec §5 "token-emission script": Task 3 (`_08_emit_skill.py`)
- Spec §6 "testing": Task 2 (`test_skill_emitter.py`)
- Spec §7 "installation procedure": Task 4 (README docs) + Task 6 (smoke test)
- Spec §8 "success criteria": validated by Tasks 2 (automated) + 6 (manual)

**Placeholder scan:** No "TBD"/"TODO"/"add appropriate X" placeholders. Every code block is concrete. The transformation map intentionally has only the most important replacements; the emitter applies them as-is, and Task 3 step 3 explicitly handles the case where additional upstream colors slip through (re-add to the JSON, re-run).

**Type consistency:** `transform_text(text, transforms)`, `rewrite_frontmatter(text, fm)`, `emit_data_viz_md()`, `emit_brand_marks_md()`, `main()` are all consistent across Task 2 (tests) and Task 3 (impl). The `EXPECTED_FILES` list in tests matches the file structure produced by the emitter.

---

## Out of scope (per spec)

- The `website/` demo from upstream — not adapted.
- Behavioral evaluation (does the agent actually produce good UIs?) — that's a manual eval workflow, not a Plan 2 deliverable.
- Plans 3, 4, 5 (Office, Google Workspace, enterprise deployment).
