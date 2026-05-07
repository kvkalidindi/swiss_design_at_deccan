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

import base64
import json
import shutil
import subprocess
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TMP_SWISS = ROOT / ".tmp_swiss" / "swiss-design"
TRANSFORMS = ROOT / "data" / "skill-transformations.json"
SKILL = ROOT / "skill"
LOGO_SRC = ROOT / "data" / "logo.png"
LOGO_RAW_URL = (
    "https://raw.githubusercontent.com/kvkalidindi/swiss_design_at_deccan/"
    "main/data/logo.png"
)

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


def emit_document_furniture_md() -> str:
    return """\
# Document Furniture — Cover, Header, Footer & End Pages

Every Deccan document — Word, PowerPoint, Excel, and PDFs exported from them — uses the same four pieces of "furniture" so brand presence is consistent across formats.

The four pieces:

1. **Cover page** (face page) — first page, self-contained: logo + title + optional subheading + author + version + date
2. **Running header** — small logo + document title, every body page (Word/PDF)
3. **Running footer** — confidentiality line + page number, every body page
4. **End page** — final page after a forced page break, centered logo + brand line

The cover and end page do **not** show the running header/footer or page numbers — they are their own self-contained compositions.

---

## Hard rules

These are non-negotiable and apply to every Word and PDF document produced from this system:

1. **Cover page is mandatory and self-contained.** Body content does not begin until the cover page has been composed. No header, footer, or page number appears on it.
2. **Cover page must include**, in this order: Deccan corporate logo, Document Title, optional Subtitle/subheading, Author / Prepared By, Version, Date. (Classification is also recommended.)
3. **Every new top-level section starts on a new page.** Each H1 carries `pageBreakBefore`; do not rely on the bottom-25% heuristic alone. The author must not override this on a per-paragraph basis.
4. **Body text fills the full live content area in print.** The web `max-w-[60ch]` rule is for screen rendering only. In Word, PowerPoint, Excel, and exported PDFs, body paragraphs run edge-to-edge of the live content area (margin-to-margin). Do not introduce manual right indents or text frames that shrink the column.
5. **Live content area ≥ 80% of paper width.** Margins must be tight enough that the live content area is at least 80% of paper width. For US Letter (8.5" wide) that means margins ≤ 0.85" on each side. The default is 0.8" giving 81.2% content width.
6. **End page always follows a page break.** Body content ends, then a hard page break, then the end page. Never share a page with body content.
7. **Footer shows the page number on every body page.** Page numbers are suppressed only on the cover and the end page. The page number is **the bare integer** (e.g. `12`), right-aligned in the footer — not "Page 12 of 47" or any other prefix/suffix.
8. **Page background is white.** Body pages use pure white (`#FFFFFF`) as the page background. The Stone palette tints (`stone-50`, `stone-100`, `stone-200`) are **only** used for explicit callout / highlight / sidebar blocks that need contrast from surrounding content — never as a general page or surface background.

---

## Logo sizing

The Deccan logo is the only image that appears across all furniture. Sizes are deliberate, not arbitrary:

| Placement | Width | Notes |
|-----------|-------|-------|
| Cover page (Word/PPT) | 2.5" / 64mm | Hero treatment |
| Running header (Word) | 0.6" / 15mm | Small mark, top-left |
| Slide footer (PowerPoint) | 0.9" / 23mm | Bottom-left corner |
| Excel print header | 0.5" / 13mm | Squeezed into header band |
| End page (all) | 1.8" / 46mm | Centered, slightly smaller than cover |

Always link the logo file rather than recolor or recompose it. Never stretch — preserve aspect ratio.

---

## Cover page

The first page of every Deccan document. **Self-contained:** no running header, no running footer, no page number. Composition (top to bottom):

1. **Top whitespace** — at least 25% of page height (the "breathing room" the Swiss style demands)
2. **Logo** — left-aligned at 2.5" / 64mm width
3. **Document title** — IBM Plex Sans Light, 36pt, Deccan Blue `#164999`
4. **Subtitle** — IBM Plex Sans Regular, 16pt, stone-900/70 (opacity). Optional but recommended for one-line summary.
5. **Accent rule** — 1pt horizontal line, full content width, Deccan Blue at 100%
6. **Metadata block** — caption-style (IBM Plex Sans 9pt uppercase, tracking-wide, stone-900/70). Required labels, in this order:
   - DOCUMENT TYPE
   - PREPARED BY *(Author info — required)*
   - DATE *(required)*
   - VERSION *(required)*
   - CLASSIFICATION
7. **Bottom whitespace**

In Word, the cover lives on page 1 of the section with "Different first page" enabled, which suppresses the running header/footer for that page. In PowerPoint, the cover is its own layout with no slide-master footer placeholders.

Body content **never begins on the cover page**. A page break separates the cover from page 2 (the first body page).

---

## Running header

Every body page of a Word document carries a slim header. The header height is fixed; content within it is rendered at low visual weight so it never competes with body content.

Layout (left to right):

| Region | Content | Style |
|--------|---------|-------|
| Left | Logo, 0.6" wide | Vertical centre |
| Right | Document title | IBM Plex Sans 9pt, stone-900/70 |

Below the header content sits a 0.5pt rule in `stone-200`. Word implements this as a single underline on the header paragraph.

Excel uses the same idea via `oddHeader` — logo on the left, sheet/workbook title on the right.

PowerPoint does not use a top header (the canvas is too wide and the cover slide treatment carries brand presence). Instead, each content slide gets a slide-footer (see below).

---

## Running footer

Every body page carries a footer with three regions:

| Region | Content |
|--------|---------|
| Left | "Deccan Chemicals · Confidential" — IBM Plex Sans 9pt, stone-900/70 |
| Center | (blank) |
| Right | Page number, bare integer (e.g. `12`) — IBM Plex Sans 9pt, stone-900/70, tabular-nums |

**Page numbers are mandatory on every body page** and rendered as the bare integer, right-aligned. Do not write "Page X" or "Page X of Y" — Word/PowerPoint/Excel and the resulting PDF all use the unadorned number. Page numbers are suppressed only on the cover and end page.

A 0.5pt rule sits **above** the footer text in stone-200, matching the header.

Confidentiality classification can be one of: `Public`, `Internal`, `Confidential`, `Restricted`. `Confidential` is the default — change it per-document, never remove the line.

PowerPoint slide footer (left to right): logo (0.9" wide) — section name — slide number. The slide footer rule is a 1pt blue-500 line at 30% opacity along the slide bottom, 0.4" from the edge.

Excel `oddFooter`: left = "Deccan Chemicals · Confidential", right = "Page &P of &N".

---

## Section flow rules (Word/PDF)

Body content must respect three flow rules so headings and sections never appear awkwardly placed:

1. **Every H1 starts on a new page.** Top-level sections always begin at the top of a fresh page. Templates enforce this by setting `pageBreakBefore=True` on the Heading 1 style. Authors must not override it.
2. **H2 / H3 headings stay with their first body paragraph.** `keepWithNext=True` on every heading style.
3. **Paragraphs do not split across pages mid-line.** `keepLinesTogether=True` on heading styles and on numbered lists. As a fallback for H2/H3, the bottom-25% heuristic still applies: if a heading lands in the bottom quarter of a page, the author inserts an explicit page break.

The point of the absolute "H1 → new page" rule is that document review is faster and more predictable when the reader knows section boundaries always coincide with page boundaries. The bottom-25% rule for sub-headings is a softer rule and lives in the author's hands.

---

## End page

The last page of every Word and PowerPoint document. **Always preceded by an explicit page break** so it never shares a page with body content. **Self-contained:** no running header, no running footer, no page number.

Composition:

1. **Vertical centering** — the content is anchored to the visual centre of the page, with substantial whitespace above and below
2. **Logo** — centered, 1.8" / 46mm width
3. **Brand line** — "Deccan Chemicals" in IBM Plex Sans Regular 14pt, centered, full-opacity stone-900
4. **Tagline / contact line** — caption style 9pt, centered, stone-900/40, single line. Default: `deccanchemicals.com · Hyderabad, India`

For Excel: a final worksheet named "End" containing the same composition (logo + brand line + tagline). Excel doesn't have a natural concept of an "end page", but a parallel sheet keeps the brand presence consistent when the workbook is paged through.

---

## Backgrounds and surfaces (print)

Print documents use **pure white** (`#FFFFFF`) for all page backgrounds. This differs from screen rendering, where the Swiss web system uses `bg-stone-50` as a default page background.

The Stone palette tints (`stone-50` `#FAFAF9`, `stone-100` `#F5F5F4`, `stone-200` `#E7E5E4`) are reserved in print for **explicit highlight or callout blocks** that must stand out from surrounding body content. Permitted uses:

- **Code blocks** (the most common — see "Code and mono text" below)
- **Inline code chips** (variable names, file paths, function names, command names — same below)
- A boxed callout / pull-quote / "key takeaway" panel
- A table's banded rows (allowed because the contrast is functional, not decorative)
- A sidebar panel that intentionally interrupts body flow

Stone tints are **never**:

- A general page background
- A wide horizontal band that spans the page just for visual texture
- Applied to every body paragraph
- Used in the running header or footer
- Applied to multi-page sections to differentiate them — that's what the H1 page break is for

If a callout block has no functional reason for its tint, drop the tint. White space is the design.

---

## Code and mono text

Any text rendered in the **monospace variant** of the type stack — IBM Plex Mono with the documented Fira Code → SFMono → Consolas fallback chain — must carry a Stone-tinted background. The mono treatment and the Stone background travel together. One never appears without the other.

**Why:** The Swiss design system's body type is a sans grotesque (IBM Plex Sans) at the body width. When a mono glyph appears mid-paragraph or in a block, the eye needs an immediate visual cue that this is a different *kind* of content — code, identifier, file path, command — not just an italic or bold variation. Stone tinting + mono font is that cue.

### Inline code (variable names, identifiers, file paths, technical tokens)

| Property | Value |
|----------|-------|
| Font | IBM Plex Mono → Fira Code → SFMono → Consolas → ui-monospace |
| Size | 0.95em of body (so ascender/descender match adjacent sans) |
| Background | `stone-100` `#F5F5F4` |
| Padding | 0.1em–0.2em horizontal in HTML; tight character shading in Word |
| Color | Same as surrounding body text (do not recolor) |

In Word, this is a **character style** named `Code Inline`. Authors apply it to runs of inline code; the style sets the font and adds character shading.

### Code blocks (multi-line code, command snippets, configuration excerpts)

| Property | Value |
|----------|-------|
| Font | IBM Plex Mono → Fira Code → SFMono → Consolas → ui-monospace |
| Size | 10pt (or the equivalent in the host context) |
| Background | `stone-100` `#F5F5F4` filling the whole block |
| Border | None (the fill is enough — Swiss is rectilinear, not "boxed") |
| Indent | Match body width — code blocks are full-width, not indented in from body |
| Spacing | 8pt above, 8pt below (aligned to the 8px grid) |
| Color | `stone-900` body text |
| Page-break | Avoid splitting a block across pages when shorter than half a page |

In Word, this is a **paragraph style** named `Code Block`. Authors apply it to entire paragraphs; the style sets the font, fill, and spacing.

### What counts as "technical token"

Apply the inline code chip to:

- Variable names: `palette`, `blue_500`, `meta`
- Function / method names: `emit_dotx()`, `build_palette()`
- File paths: `scripts/lib/office_docx.py`, `~/.claude/settings.json`
- Command names and shell snippets: `git push`, `python -m pytest`
- Environment variables: `SEMGREP_APP_TOKEN`, `PATH`
- Data-format keywords: `JSON`, `null`, `true` (when discussed *as* JSON tokens, not as English words)

Do **not** apply it to:

- Brand or product names (those use sans regular: "GitHub", "Word", "Claude")
- Acronyms in body prose ("PDF", "API")
- Numeric values quoted in body text ("the build is 49,972 bytes")

### Format-specific implementation

- **Word (.dotx)**: ships with `Code Inline` (character style) and `Code Block` (paragraph style) registered in the styles part. Pre-styled.
- **PowerPoint (.potx)**: a slide-master text layout placeholder labelled "Code" uses the same mono+stone treatment. Authors paste code into that placeholder, not into normal body text frames.
- **Excel (.xltx)**: a named cell style "Code" applies IBM Plex Mono + stone-100 fill. Use it on cells that contain command snippets, formulas, or technical IDs.
- **PDF**: inherits from the Word/PowerPoint/Excel source.

---

## Page setup

| Paper | Margins | Content width | % of paper |
|-------|---------|---------------|------------|
| US Letter (8.5" × 11") | 0.8" all sides | 6.9" | 81.2% |
| A4 (210mm × 297mm) | 20mm all sides | 170mm | 81.0% |

Header distance: 0.5" from top edge. Footer distance: 0.5" from bottom edge.

These are the **maximum** margin widths. Tighter (more content) is acceptable; looser (less content) is not — the 80% rule is a floor, not a target.

---

## When to skip the furniture

The furniture is the default. You may skip it only when the document is genuinely transient or a fragment:

- Single-page memos under one page of body text — cover page is overkill
- Embedded Excel ranges shipped as figures inside a Word doc — the host already has furniture
- One-pagers / leave-behinds explicitly designed without it (a deliberate brand choice)

When in doubt, include the furniture. Brand presence is cheap; absence is conspicuous.

---

## File-format reference

| Format | Cover | Header | Footer (page #) | End |
|--------|-------|--------|-----------------|-----|
| Word (`deccan.dotx`) | Page 1 with "different first page" — no header/footer | Section header on body pages | Section footer with `PAGE` field on body pages only | New section after explicit page break, header/footer cleared |
| PowerPoint (`deccan.potx`) | Dedicated cover slide layout | (none — cover does the work) | Slide-master footer with slide number on content slides only | Dedicated end slide layout, no footer |
| Excel (`deccan.xltx`) | "Cover" sheet (no print header/footer) | `oddHeader` print region on data sheets | `oddFooter` print region on data sheets only | "End" sheet (no print header/footer) |
| PDF | Carried over from the source doc | Carried over | Carried over | Carried over |

PDFs are not authored directly — they're exports of the Office formats — so applying furniture to the source files automatically propagates to the PDF.

---

## Rendering and verifying templates

To visually verify a generated `.dotx` / `.potx` / `.xltx`, render it to PDF and open the PDF.

**Recommended path (deterministic, no automation surprises):**

1. Open the template in the corresponding Office app (Word, PowerPoint, Excel).
2. **File → Export → Create PDF/XPS** (or **File → Save As → PDF**).
3. Save into `outputs/template_previews/` (gitignored).

**Why not COM automation?** On managed corporate Windows installs (this user's environment included), `Word.Application` / `PowerPoint.Application` / `Excel.Application` COM objects can hang silently on first launch waiting for a Trust Center prompt, license activation, or first-run dialog that never reaches the foreground because `Visible = $false`. The render call appears to "work" but never returns. If you must automate, use **LibreOffice headless** (`soffice --headless --convert-to pdf <file>`) or **`libreoffice` in WSL** instead, both of which are deterministic and dialog-free.

**What to look for in the rendered PDF:**

- Cover page is page 1 with no header/footer/page number.
- Body content begins on page 2.
- Header (logo + title) and footer ("Deccan Chemicals · Confidential" + "Page X of Y") appear on every body page.
- No heading lands in the bottom 25% of any page.
- End page is the final page, alone, with no header/footer/page number.
- Live content area is at least 80% of paper width.

If any of these fail, the regression is in the emitter (`scripts/lib/office_*.py`), not the document — fix the source and re-emit.
"""


def emit_logo_assets() -> tuple[Path, Path, str]:
    """Bundle the corporate logo into the skill so emitters never have to fetch
    it from the network.

    Returns (logo_png_path, logo_b64_path, base64_str)."""
    assets = SKILL / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    logo_png = assets / "logo.png"
    shutil.copy(LOGO_SRC, logo_png)

    raw_bytes = LOGO_SRC.read_bytes()
    b64 = base64.b64encode(raw_bytes).decode("ascii")
    logo_b64 = assets / "logo.b64.txt"
    logo_b64.write_text(
        "# Deccan corporate logo, base64-encoded PNG.\n"
        "# Use as a data URI: `data:image/png;base64,<contents below>`\n"
        "# Source of truth: data/logo.png in the swiss_design_at_deccan repo.\n"
        + "\n".join(textwrap.wrap(b64, 76)) + "\n",
        encoding="utf-8",
    )
    return logo_png, logo_b64, b64


def emit_logo_asset_md(b64: str, png_size_bytes: int) -> str:
    # Show only the first 96 chars of base64 inline; the full payload lives in
    # skill/assets/logo.b64.txt to keep this reference file small.
    b64_preview = b64[:96] + "…"
    return f"""\
# Logo Asset — Reliable Retrieval

The Deccan corporate logo is the only image that appears in document furniture (cover pages, headers, end pages, signatures). Every artifact emitter — local Python scripts, Claude Code, Claude.ai web/mobile, Office templates — must be able to obtain it deterministically. This reference defines the canonical retrieval order so a transient network failure can never block document generation.

## Source of truth

The single source of truth is **`data/logo.png`** in the [swiss_design_at_deccan](https://github.com/kvkalidindi/swiss_design_at_deccan) repository.

- Format: PNG, 185 × 60 px, 8-bit/color RGBA, non-interlaced
- Size: ~{png_size_bytes:,} bytes
- Aspect ratio: ~3.08 : 1 (wider than tall)

Never recolor, recompose, stretch, or rasterize a different version. If the source ever changes, update only `data/logo.png` and re-run `python -m scripts._08_emit_skill` to propagate to all skill assets.

## Retrieval order

When an emitter needs the logo, it tries these sources **in this order** and stops at the first one that succeeds:

1. **Skill-bundled file** — `skill/assets/logo.png` (relative to the skill root). Always present once the skill is loaded; no network required.
2. **Project-local file** — `data/logo.png` in the working tree. Used by local scripts running inside the repo.
3. **Stable raw URL** — `{LOGO_RAW_URL}` — public, no auth, served by GitHub's raw CDN. Use only when neither of the above is available, e.g., a Claude.ai conversation that doesn't have the skill bundle materialized as files.
4. **Inline base64 fallback** — `skill/assets/logo.b64.txt` contains the full PNG as a single base64 string (for embedding into HTML/SVG/CSS as a `data:image/png;base64,…` URI). Use when the runtime can't read binary files but can read text.

The stable raw URL is the single network endpoint we commit to keeping live. It is **public**, requires no authentication, and is served from GitHub's CDN — far more reliable than fetching `https://www.deccanchemicals.com/...` directly, which can rate-limit, redirect, or change.

## For Claude.ai (web/mobile)

Claude.ai conversations don't always have the same skill-bundle file access as Claude Code. When generating an HTML/SVG/PDF artifact, prefer the embedded base64 data URI:

```html
<img src="data:image/png;base64,{b64_preview}"
     alt="Deccan Chemicals" width="185" height="60">
```

The full base64 payload is in `skill/assets/logo.b64.txt` (it is too large to inline in this reference). Read that file and substitute the body of the data URI. The result is a self-contained artifact with **zero** network dependencies.

If you cannot read the asset file, use the stable raw URL above as the `src` instead. Do **not** attempt to fetch from `deccanchemicals.com` directly — that domain is not committed to as a stable image source.

## For Word / PowerPoint / Excel emitters

Local Python emitters (`scripts/lib/office_*.py`) read `data/logo.png` directly via `Path` and `add_picture(...)`. No network round-trip. Do not introduce a `requests.get(...)` call — the file is always present in the repo.

## For HTML/CSS artifacts

For HTML emitters that ship as a single self-contained file (email signatures, downloadable design briefs):

- Use the base64 data URI (Option 4 above). This is what `office_signature.py` and the design-brief HTML do today.

For HTML pages on a Deccan-hosted site:

- Reference `/assets/logo.png` (host-relative). The publishing pipeline copies `data/logo.png` to the public `/assets/` path during deploy.

## What "fetch the logo from the web" should never mean

If an emitter says "fetch the logo from the web," that is a bug. The retrieval order above is exhaustive. The stable raw GitHub URL is a *fallback*, not a primary path. `deccanchemicals.com` is **never** a source — even if a script worked once by hitting it, that script must be rewritten to use the bundled asset.

## Update procedure

When the corporate logo changes:

1. Replace `data/logo.png` with the new master.
2. Run `python -m scripts._08_emit_skill` — this regenerates `skill/assets/logo.png` and `skill/assets/logo.b64.txt`.
3. Run `python -m scripts._09_emit_office` — this regenerates the Office templates and the signature with the new logo.
4. Commit and push to `main` — the stable raw URL automatically reflects the new file.
5. Re-deploy the skill to local Claude profile and Claude.ai.
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
    (SKILL / "references" / "document-furniture.md").write_text(emit_document_furniture_md(), encoding="utf-8")

    _, _, b64 = emit_logo_assets()
    (SKILL / "references" / "logo-asset.md").write_text(
        emit_logo_asset_md(b64, LOGO_SRC.stat().st_size), encoding="utf-8"
    )

    print("Generated:")
    for p in sorted(SKILL.rglob("*.md")):
        rel = p.relative_to(SKILL)
        size = p.stat().st_size
        print(f"  skill/{rel} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
