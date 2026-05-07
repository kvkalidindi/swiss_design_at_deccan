# Document Template — Deterministic Cover, Body, End

When generating a Word-equivalent or PDF document under the swiss_design_at_deccan system, fill the bundled template rather than re-deriving the layout from prose. The template is the single source of truth for cover composition, running header and footer, end-page layout, code styling, and the eight hard rules in `references/document-furniture.md`.

## Source of truth

`skill/assets/templates/document.html` — a self-contained HTML5 file. The published artifact at the stable raw GitHub URL is rendered from `data/templates/document.template.html` with the corporate logo inlined as a base64 data URI, so a consumer fetching the URL receives one file with no further binary dependencies for the brand mark.

The template includes:

- A Google Fonts `@import` for IBM Plex Sans (italic + weights 300/400/500/600) and IBM Plex Mono (weights 400/500/700). Chromium fetches Google Fonts at print time without an additional tool call. A secondary `@font-face` fallback pointing at the bundled WOFF2s in `skill/assets/fonts/` is included for offline / self-hosted environments.
- Brand colour tokens (`--accent: #164999`, stone palette, ink opacity tokens).
- `@page` rules implementing the running header and footer on body pages and suppressing both on cover and end pages.
  - Top-left: `DECCAN FINE CHEMICALS` set in caption-style brand caps, Deccan Blue.
  - Top-right: the document title, captured via CSS `string-set` on the cover title and rendered via `content: string(doc-title)` on each body page.
  - Bottom-left: `Deccan Fine Chemicals · ` followed by the classification.
  - Bottom-right: bare-integer page number.
- The corporate logo inlined as a data URI on the cover (2.5") and end page (1.8"). No external fetch.
- A cover composition matching the spec: 2.5" logo top-left, 36pt light Deccan Blue title, 16pt subtitle, full-width accent rule, five-row metadata block (DOCUMENT TYPE, PREPARED BY, DATE, VERSION, CLASSIFICATION).
- Heading rules: `h1` is 28pt, font-weight 300, Deccan Blue, with `page-break-before: always` so every section starts on a new page.
- Code styling: inline `<code>` and `.code-inline` use IBM Plex Mono on a stone-100 chip; `<pre>` and `.code-block` use full-width stone-100 panels.
- End page composition: centered logo, "Deccan Fine Chemicals" brand line, contact line at low opacity.

## Renderer compatibility

The template targets the lowest common denominator of the renderers that produce Deccan PDFs in practice:

| Renderer | Where it runs | Status |
|----------|---------------|--------|
| Headless Chromium / Puppeteer | The Claude.ai cloud PDF runtime; modern browsers (Save as PDF) | Fully supported. Fonts, logo, headers, and footers all render. |
| WeasyPrint | Local Python pipelines on a workstation | Fully supported. The bundled WOFF2 fallback applies if Google Fonts is unreachable. |
| Prince | High-end print pipelines | Fully supported. |

Earlier template revisions used CSS Paged Media `position: running()` and `content: element()` for the running header. Those features are present in WeasyPrint and Prince but absent in Chromium, so the running header was invisible in Chromium-rendered PDFs. The current template uses `string-set` and `string()` instead, which Chromium implements.

## Slot placeholders

String-replace these before rendering. `{{LOGO_DATA_URI}}` is **not** a consumer slot — it is substituted by the skill emitter at publication time and is already inlined in the published artifact at the raw GitHub URL.

| Slot | Content |
|------|---------|
| `{{TITLE}}` | Document title |
| `{{SUBTITLE}}` | Optional one-line subhead |
| `{{DOCUMENT_TYPE}}` | "Standard", "Report", "Brief", "Policy" |
| `{{PREPARED_BY}}` | Author or office |
| `{{DATE}}` | Free-form date string |
| `{{VERSION}}` | Version string (e.g. `1.0`) |
| `{{CLASSIFICATION}}` | `Public`, `Internal`, `Confidential`, or `Restricted` |
| `{{BODY_HTML}}` | The document body, as HTML |

The body uses standard HTML5: `<h1>`, `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<table>`, `<code>`, `<pre><code>`. The template CSS does the rest.

## Retrieval

In retrieval-cascade order, first source that succeeds wins:

1. Skill-bundled file at `skill/assets/templates/document.html` — always present once the skill is loaded.
2. Project-local file at `skill/assets/templates/document.html` in the working tree.
3. Stable raw URL: `https://raw.githubusercontent.com/kvkalidindi/swiss_design_at_deccan/main/skill/assets/templates/document.html` — public, served by GitHub's CDN. The brand logo is already inlined as a data URI in this file.
4. Inline copy pasted directly into the artifact.

## Rendering paths

- **Claude.ai cloud sessions**: fetch the template from the stable raw URL. Fonts load from Google Fonts at print time (Chromium fetches them automatically). The logo is already inlined as a data URI. No further fetches required.
- **Claude Code / local Python emitters**: copy the template, run a local templating step (Jinja2, plain string replacement, or otherwise), open the rendered HTML in a browser and use Save as PDF, or feed to WeasyPrint or wkhtmltopdf for headless rendering. If Google Fonts is blocked at the corporate egress layer, the bundled `skill/assets/fonts/*.woff2` fallback applies.
- **Word output**: this template is for HTML/PDF only. For native `.dotx`/`.docx` use the Office templates in `office/templates/deccan.dotx`, which encode the same rules in styles.xml.

## Conformance

The template implements every hard rule in `document-furniture.md`:

- Self-contained cover with logo, title, subtitle, prepared-by, date, version, classification.
- Cover has no header, footer, or page number (`@page cover-page` clears them).
- Every `<h1>` starts on a new page (`page-break-before: always`).
- Body fills the full live content area (no `max-w-60ch` restriction).
- 0.8" margins on Letter give 6.9" / 8.5" = 81.2% live content area.
- End page follows an explicit page break (`page-break-before: always` on `.end`).
- Footer page number is the bare integer (`content: counter(page)`).
- White page background; stone tints reserved for `.code-inline`, `.code-block`, `.callout`, `table.banded`.

Do not modify the structural CSS without re-checking each rule against `document-furniture.md`. Do not add a second accent colour. Do not apply stone tints anywhere outside the four allowed selectors.
