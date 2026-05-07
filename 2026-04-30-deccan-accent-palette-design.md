# Deccan Fine Chemicals Design System — Accent Color Palette & Multi-Format Foundation

**Date:** 2026-04-30
**Owner:** kishore.kalidindi@deccanchemicals.com
**Status:** Draft for review

---

## 1. Background & Goal

Deccan Fine Chemicals is rebuilding its corporate website from scratch and adopting a comprehensive design system that will govern all company collateral—web, documents, print, and brand materials.

The chosen foundation is **swiss-design-skill** (zeke/swiss-design-skill on GitHub), a Swiss-design-principles design skill currently focused on web UI with Tailwind CSS. We will:

1. **Replace** its accent color palette with a brand-derived 8-step accent palette extracted from the Deccan Fine Chemicals corporate logo.
2. **Extend** the design system beyond web UI to support Microsoft 365, Google Workspace, and print/brand collateral.
3. **Substitute** any commercially-licensed fonts in the original skill with the closest free Google Fonts equivalents.
4. **Deploy** the final system to all corporate Windows 11 PCs so that Office, browsers, and design tools default to brand-compliant settings.

The deliverable is a modified swiss-design-skill that becomes the official Deccan Fine Chemicals design guideline.

---

## 2. Color Extraction Methodology

**Source:** Deccan Fine Chemicals corporate logo, retrieved from https://deccanchemicals.com

**Process:**
1. Fetch the live website and locate the logo asset (PNG or SVG in the header).
2. Apply color quantization to extract the 6 dominant brand colors (4 blues + 2 greens), excluding background/whitespace pixels.
3. Capture each color's hex, RGB, HSL, CMYK, and recommended Pantone (PMS) values.
4. Group colors into two families:
   - **Blue family:** 4 anchor candidates
   - **Green family:** 2 anchor candidates

**Output:** A canonical "logo color manifest" listing all 6 colors with measured values across all color spaces.

---

## 3. Palette Structure (8 Steps)

A dual-family system with 4 steps each, following lightness progression conventions used by Tailwind, Material, and Radix UI:

| Step | Role | Typical Use |
|------|------|-------------|
| `blue-100` / `green-100` | Lightest tint | Backgrounds, hover fills, subtle highlights |
| `blue-300` / `green-300` | Light | Borders, dividers, secondary accents |
| `blue-500` / `green-500` | **Anchor** (logo-derived) | Primary buttons, links, brand identity |
| `blue-700` / `green-700` | Dark | Hover/pressed states, emphasis |

The `-500` step in each family is the most-prominent logo blue and most-prominent logo green, preserving brand authenticity at the anchor.

**Out of scope for this palette:** Status colors (success, warning, info, error) — these will use a traditional multi-colored palette, defined separately in the design system.

---

## 4. Step Generation Logic (Hybrid: Extract + Anchor + Refine)

For each color family, generate the 4 steps using a combination of logo-derived anchors and HSL adjustments.

**Blue family (4 logo shades available):**
- `blue-500` (anchor) → most-saturated/dominant blue from the logo
- `blue-700` → darkest logo blue (or darken anchor by ~15% lightness if too close)
- `blue-300` → second-lightest logo blue (or generate by lightening anchor ~15%, desaturating ~10%)
- `blue-100` → generate by lightening anchor to ~92–95% lightness

**Green family (only 2 logo shades available):**
- `green-500` (anchor) → more-saturated logo green
- `green-700` → second logo green (assuming darker), or darken anchor by ~15% lightness
- `green-300` → generate by lightening anchor ~15% with slight desaturation
- `green-100` → generate by lightening anchor to ~92–95% lightness

**Validation rules:**
- WCAG AA contrast ratio ≥ 4.5:1 when used for text on white or dark backgrounds
- Minimum 12% lightness gap between adjacent steps (avoids visually-identical colors)
- Manual visual review at the end to nudge any step that feels off

---

## 5. Multi-Format Design System Integration

The modified swiss-design-skill becomes a **format-agnostic design system** with platform-specific implementations.

**Core layer (format-agnostic):**
- Color tokens defined as semantic concepts: `accent-blue-anchor`, `accent-blue-light`, etc.
- Typography, spacing, and grid principles articulated in Swiss design language
- Each color expressed in multiple color spaces:
  - Hex / RGB / HSL → web, digital UI
  - CMYK → print materials
  - Pantone (PMS) → professional print, signage, branded merchandise

**Platform-specific layers:**
1. **Web/Tailwind** — Tailwind config + CSS variables (replaces existing swiss-design-skill web layer)
2. **Document** — Microsoft Word/PowerPoint/Excel themes, Google Docs/Slides templates with palette pre-loaded
3. **Print/collateral** — Adobe ASE (swatch exchange) file for InDesign/Illustrator + PDF brand guidelines

**`palette.json` structure:**
```json
{
  "blue": {
    "500": {
      "hex": "#...",
      "rgb": "rgb(...)",
      "hsl": "hsl(...)",
      "cmyk": "cmyk(...)",
      "pantone": "PMS ..."
    }
  }
}
```

---

## 6. Font Strategy & Google Fonts Substitution

The swiss-design-skill is rooted in classic Swiss typography and likely prescribes commercial fonts (Helvetica, Akzidenz-Grotesk, Univers, Neue Haas Grotesk) requiring costly licenses that block enterprise-wide deployment.

**Substitution criteria for each commercial font:**
- Geometry/proportions (x-height, letter width, terminals)
- Weight range available (Swiss design uses many weights for hierarchy)
- Variable font support (preferred for performance and flexibility)
- Latin + extended-Latin coverage (international business contexts)
- Open license permitting redistribution (SIL OFL or similar)

**Anticipated substitutions (to be confirmed during audit):**

| Original (Commercial) | Google Fonts Alternative | Rationale |
|---|---|---|
| Helvetica / Helvetica Neue | Inter | Designed for screens, full weight range, near-identical metrics |
| Akzidenz-Grotesk | Manrope or Work Sans | Similar humanist-grotesque feel |
| Univers | DM Sans | Geometric grotesque with variable axes |
| Neue Haas Grotesk | Inter or Plus Jakarta Sans | Closest digital re-interpretations |

A `typography.md` document captures each substitution with licensing notes and side-by-side comparisons.

---

## 7. Enterprise Deployment Strategy

Goal: Word, PowerPoint, browsers, and Google Workspace default to the new design system on every corporate PC.

**Microsoft 365 (Windows 11):**
1. **Office theme package** — `.thmx` files for Word/PowerPoint/Excel loading palette as theme colors and Google Fonts as theme fonts
2. **Document templates** — `.dotx` (Word), `.potx` (PowerPoint), `.xltx` (Excel) with cover pages, heading styles, body styles pre-applied
3. **Email signature templates** — HTML signature for Outlook with brand-compliant typography and color
4. **Font installation** — Google Fonts packaged as `.ttf`/`.otf` files (SIL OFL permits redistribution)

**Deployment mechanism:**
- **Microsoft Intune** (preferred) — Push fonts, templates, Office settings via configuration profiles
- **Group Policy** (alternative) — Deploy fonts to `C:\Windows\Fonts` and templates to user/workgroup template paths
- **Default Office settings** — Configure Office's default font/theme via registry keys or Office Customization Tool

**Google Workspace:**
1. **Slides/Docs templates** — Branded masters published to organization's template gallery (admins can pin them)
2. **Google Fonts integration** — Workspace already supports Google Fonts natively
3. **Admin Console branding** — Apply colors to login pages, Gmail headers where customization is permitted

**Browser defaults:**
- Configure Chrome/Edge default font preferences via Group Policy / Intune for fallback rendering
- Internal corporate sites link to Google Fonts CDN or self-hosted equivalents

---

## 8. Deliverables (Final List)

| # | File | Purpose |
|---|------|---------|
| 1 | `palette.md` | Multi-format color documentation, use cases, accessibility notes |
| 2 | `typography.md` | Font substitutions + licensing notes + comparisons |
| 3 | `palette.json` | All color spaces, machine-readable |
| 4 | `palette.css` | CSS variables + Tailwind config snippet |
| 5 | `palette.ase` | Adobe Swatch Exchange file for InDesign/Illustrator/Photoshop |
| 6 | `palette-swatches.html` | Visual preview with all 8 colors |
| 7 | `office-theme.thmx` | Microsoft Office theme |
| 8 | `templates/*.dotx, *.potx, *.xltx` | Word/PowerPoint/Excel starter templates |
| 9 | `fonts/` | Packaged Google Font files |
| 10 | `deployment-guide.md` | Intune/GPO deployment instructions for IT |
| 11 | `gworkspace-templates/` | Google Slides/Docs templates + admin setup guide |

---

## 9. Success Criteria

- An employee opening Word or PowerPoint on a corporate PC sees the brand fonts and theme colors as defaults.
- A developer cloning the modified swiss-design-skill repo gets a complete web UI design system that drops into a Tailwind project.
- A designer opening Adobe Illustrator can load the `.ase` swatch file directly.
- Marketing can produce print materials with accurate CMYK and Pantone references.
- The new website built on this design system is brand-coherent end-to-end.
- All 8 accent colors meet WCAG AA contrast requirements when used for their documented purposes.

---

## 10. Open Questions (Resolved During Implementation)

- Exact hex values of the 6 logo colors (depends on the actual logo asset)
- Final font list from swiss-design-skill (depends on the repo audit)
- Whether the Pantone values can be derived algorithmically or require professional reference (Pantone bridge guides may be needed for exact matches)
- Intune vs Group Policy availability in the Deccan Fine Chemicals IT environment
- Existing Microsoft 365 / Google Workspace tenant admin access for the deployment

These are resolved during the implementation phase and recorded in the implementation plan.

---

## 11. Out of Scope

- Logo redesign (we work with the existing logo as-is)
- Status indicator color palette (success/warning/info/error) — defined separately
- Photography style guide, illustration style guide, motion guidelines — future design system extensions
- Localization beyond Latin scripts (the corporate context determines if/when this is needed)
- Hosting and DNS for the new website itself (this spec covers the design system, not infrastructure)

---

## 12. Next Step

After user approval of this spec, invoke the `superpowers:writing-plans` skill to produce a detailed implementation plan that sequences:

1. Logo color extraction
2. Palette generation and validation
3. swiss-design-skill repo audit (fonts, current accents, structure)
4. Multi-format token file generation
5. Office theme + template production
6. Google Workspace template production
7. Intune/GPO deployment guide
8. End-to-end smoke test on a corporate PC
