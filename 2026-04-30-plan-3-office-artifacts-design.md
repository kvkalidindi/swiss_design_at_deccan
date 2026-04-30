# Plan 3: Microsoft Office Artifacts — Design Spec

**Date:** 2026-04-30
**Owner:** kishore.kalidindi@deccanchemicals.com
**Status:** Approved (brainstorm 2026-04-30)
**Predecessors:** Plan 1 (v0.1.0 palette + fonts), Plan 2 (v0.2.0 swiss-design skill)

---

## 1. Goal

Produce Microsoft Office artifacts so corporate Word, PowerPoint, Excel, and Outlook usage defaults to the Deccan design system: a `.thmx` theme, three branded templates (one per app), and an HTML email signature.

This is the **content** layer. Distribution to corporate fleets (Group Policy / Intune) is Plan 5 territory and out of scope here.

---

## 2. Inputs

- `outputs/palette.json` — canonical 8-step palette (Plan 1)
- `data/logo.png` — corporate logo (185×60 RGBA)
- `fonts/ibm-plex-sans/` and `fonts/ibm-plex-mono/` — TTF files for embedding
- Stone neutrals from upstream swiss-design skill (`#FAFAF9`, `#1C1917`, `#44403C`)

---

## 3. Tooling

**Python with `python-pptx`, `python-docx`, `openpyxl`** (mature, OOXML-correct libraries). Direct OOXML XML manipulation rejected as too brittle. The "hand-craft a master in Office, patch programmatically" approach was considered and rejected — it adds operational overhead (binary file in git, diff-unfriendly, hard to evolve).

A single emitter script `scripts/_09_emit_office.py` reads inputs, produces all 4 deliverables in one run, and is idempotent.

---

## 4. Theme — `office/office-theme.thmx`

Office's theme has 12 color slots. Mapping:

| Slot | Hex | Source |
|---|---|---|
| `bg1` | `#FFFFFF` | white |
| `bg2` | `#FAFAF9` | stone-50 |
| `text1` | `#1C1917` | stone-900 |
| `text2` | `#44403C` | stone-700 |
| `accent1` | `#164999` | **blue-500 — primary** |
| `accent2` | `#0C2956` | blue-700 |
| `accent3` | `#0EA3DD` | blue-300 |
| `accent4` | `#71BF4D` | green-500 |
| `accent5` | `#4F8D33` | green-700 |
| `accent6` | `#A1CB8D` | green-300 |
| `hlink` | `#164999` | blue-500 |
| `folHlink` | `#0C2956` | blue-700 |

Theme fonts:
- `majorFont` (headings) = IBM Plex Sans
- `minorFont` (body) = IBM Plex Sans

(IBM Plex Mono used inline in templates for code blocks; not a theme font.)

---

## 5. Templates

### `office/templates/deccan.dotx` (Word)
- Cover page: title, subtitle, date, author placeholder + logo (top-left)
- Executive summary block
- Body styles: H1–H4 (IBM Plex Sans, accent1), Body, Caption, Quote, Code (IBM Plex Mono)
- Page header (logo) + footer (page numbers + "Deccan Chemicals — Confidential" placeholder)
- Auto-generated table-of-contents style
- Appendix section style

### `office/templates/deccan.potx` (PowerPoint)
- 8 slide masters: Title, Section Divider, Content (1-col), Content (2-col), Content (3-col), Data/Chart, Image-Focused, Closing
- Logo bottom-right on all non-title slides
- Title slide: large logo, deep navy background, IBM Plex Sans display weight
- Sample chart on Data slide using accent1 + accent4 (blue + green) — brand-compliant data viz default

### `office/templates/deccan.xltx` (Excel)
- Title row (Deccan blue background, white IBM Plex Sans)
- Section headers (deep navy)
- Pre-formatted data table style (alternating stone-50 row banding)
- Chart-ready cells (named ranges for typical chart input)
- Footer row

### `office/templates/signature.htm` (Outlook)
- HTML email signature template
- Logo (top, ~150px wide)
- Name / role / department placeholders
- Phone, email, deccanchemicals.com link
- IBM Plex Sans inline (system-ui fallback for clients that strip styles)
- Compatibility-tested for Outlook desktop and OWA

---

## 6. Font embedding

**All 3 templates embed IBM Plex Sans (300, 400, 500, 600, 700) and IBM Plex Mono (400, 500).** Adds ~5–6 MB per template but guarantees correct rendering on machines without the fonts installed. SIL OFL 1.1 permits embedding.

---

## 7. Output directory

```
swiss_design_at_deccan/
├── scripts/
│   └── _09_emit_office.py
├── office/
│   ├── office-theme.thmx
│   ├── templates/
│   │   ├── deccan.dotx
│   │   ├── deccan.potx
│   │   ├── deccan.xltx
│   │   └── signature.htm
│   └── README.md
└── tests/
    └── test_office_emitter.py
```

`office/README.md` documents install paths per app:

| Artifact | Install location (Windows) |
|---|---|
| `office-theme.thmx` | `%APPDATA%\Microsoft\Templates\Document Themes\` |
| `deccan.dotx` | `%APPDATA%\Microsoft\Templates\` |
| `deccan.potx` | `%APPDATA%\Microsoft\Templates\` |
| `deccan.xltx` | `%APPDATA%\Microsoft\Templates\` |
| `signature.htm` | Copy/paste into Outlook signature settings |

---

## 8. Testing

- **Unit (`tests/test_office_emitter.py`):**
  - Theme XML contains all 12 color slot values
  - Each template file is a valid ZIP (OOXML format check)
  - Each template has IBM Plex Sans referenced in fonts table
  - Logo image embedded in expected places
  - Emitter is idempotent (re-running produces byte-identical files)
- **Integration (manual):**
  - Open each template in actual Word/PowerPoint/Excel; confirm theme colors render and styles work
  - Apply theme `.thmx` from Design → Themes; confirm it appears in custom themes
  - Paste signature.htm into Outlook compose; confirm HTML renders correctly

---

## 9. Out of scope (deferred to Plan 5)

- Auto-installation via Group Policy / Intune
- Setting templates as Office defaults via registry/admin policy
- Outlook signature auto-population from Active Directory
- Multi-language localization
- Dark-mode-aware templates

---

## 10. Success criteria

1. Double-clicking `deccan.dotx` opens Word with a Deccan-branded blank document.
2. Same for `.potx` (PowerPoint) and `.xltx` (Excel).
3. `office-theme.thmx` installs to Office's theme directory and appears in Design → Themes.
4. `signature.htm` pasted into Outlook displays the Deccan logo and typography correctly.
5. Documents created from these templates render identically on machines without IBM Plex installed (embedding works).
6. Emitter is idempotent and re-runs cleanly when palette evolves.

---

## 11. Open questions (resolved during implementation)

- Whether `python-pptx` supports custom slide masters cleanly, or if we need to start from a hand-crafted master.pptx and patch (research during Task 1).
- Whether font embedding via `python-docx`/`python-pptx` is fully supported or requires post-processing the OOXML (research during Task 1).
- Logo positioning DPI and exact px coordinates per template (calibration during implementation).

---

## 12. Next step

Invoke `superpowers:writing-plans` to produce the implementation plan covering:
1. Tooling research + emitter scaffolding
2. Theme `.thmx` generation
3. Word `.dotx` generation
4. PowerPoint `.potx` generation
5. Excel `.xltx` generation
6. Outlook `signature.htm` template
7. Tests + manual integration test
8. README + tag v0.3.0
