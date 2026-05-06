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
3. **No section starts in the bottom 25% of the print area.** If a new content section (any heading H1/H2) would land in the bottom quarter of the page, force a page break so it begins at the top of the next page.
4. **Content width ≥ 80% of the print area.** Margins must be tight enough that the live content area is at least 80% of paper width. For US Letter (8.5" wide) that means margins ≤ 0.85" on each side. The default is 0.8" giving 81.2% content width.
5. **End page always follows a page break.** Body content ends, then a hard page break, then the end page. Never share a page with body content.
6. **Footer shows page numbers on every body page.** Page numbers are suppressed only on the cover and the end page. Never anywhere in between.

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
| Right | "Page X of Y" — IBM Plex Sans 9pt, stone-900/70, tabular-nums |

**Page numbers are mandatory on every body page.** They are suppressed only on the cover and end page.

A 0.5pt rule sits **above** the footer text in stone-200, matching the header.

Confidentiality classification can be one of: `Public`, `Internal`, `Confidential`, `Restricted`. `Confidential` is the default — change it per-document, never remove the line.

PowerPoint slide footer (left to right): logo (0.9" wide) — section name — slide number. The slide footer rule is a 1pt blue-500 line at 30% opacity along the slide bottom, 0.4" from the edge.

Excel `oddFooter`: left = "Deccan Chemicals · Confidential", right = "Page &P of &N".

---

## Section flow rules (Word/PDF)

Body content must respect three flow rules so headings and sections never appear awkwardly placed:

1. **No new section in the bottom 25%.** If a new H1 or H2 would start in the bottom quarter of the print area, force a page break first. Authors and templates implement this by setting `pageBreakBefore` on H1 styles and `keepWithNext` + `keepLinesTogether` on all heading styles, plus a generous `space_before` on H1.
2. **Headings stay with their first body paragraph.** Set `keepWithNext=True` on every heading style.
3. **Paragraphs do not split across pages mid-line.** Set `keepLinesTogether=True` on heading styles and on numbered lists.

The 25% rule is enforced *visually* during review. Templates set the heading-style flags above so Word's layout engine pushes a heading to the next page when there is insufficient room. If after that a heading still lands in the bottom quarter, the author must insert an explicit page break.

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
