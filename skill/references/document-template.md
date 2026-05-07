# Document Template — Deterministic Cover, Body, End

When generating a Word-equivalent or PDF document under the swiss_design_at_deccan system, **fill the bundled template** rather than re-deriving the layout from prose. The template is the single source of truth for cover composition, running header / footer, end-page layout, code styling, and the eight hard rules in `references/document-furniture.md`.

## Source of truth

`skill/assets/templates/document.html` — a single self-contained HTML5 file with:

- `@font-face` rules for IBM Plex Sans (variable, weights 100-700) and IBM Plex Mono (Regular + Bold)
- Brand colour tokens (`--accent: #164999`, stone palette, ink opacity tokens)
- `@page` rules implementing the running header (logo + doc title + thin rule), the running footer (`Deccan Chemicals · {{CLASSIFICATION}}` + bare-integer page number), and suppressed furniture on cover/end pages
- A cover composition matching the spec exactly: 2.5″ logo top-left, 36pt light Deccan Blue title, 16pt subtitle, full-width accent rule, 5-row metadata block (DOCUMENT TYPE / PREPARED BY / DATE / VERSION / CLASSIFICATION)
- Heading rules: `h1` is 28pt, font-weight 300, Deccan Blue, with `page-break-before: always` so every section starts on a new page
- Code styling: inline `<code>` and `.code-inline` get IBM Plex Mono + stone-100 chip; `<pre>` and `.code-block` get full-width stone-100 panels
- An end page composition matching the spec: centered logo, "Deccan Chemicals" brand line, contact line at low opacity

## Slot placeholders

String-replace these before rendering:

| Slot | Content |
|------|---------|
| `{{TITLE}}` | Document title |
| `{{SUBTITLE}}` | Optional one-line subhead |
| `{{DOCUMENT_TYPE}}` | "Standard", "Report", "Brief", "Policy", etc. |
| `{{PREPARED_BY}}` | Author or office |
| `{{DATE}}` | Free-form date string |
| `{{VERSION}}` | Version string (e.g. `1.0`) |
| `{{CLASSIFICATION}}` | `Public`, `Internal`, `Confidential`, or `Restricted` |
| `{{BODY_HTML}}` | The document body, as HTML |

The body uses standard HTML5: `<h1>`, `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<table>`, `<code>`, `<pre><code>`. The template's CSS does the rest.

## Retrieval

Same four-source cascade as the logo, in this order:

1. **Skill-bundled file** — `skill/assets/templates/document.html` (always present)
2. **Project-local file** — `skill/assets/templates/document.html` in the working tree (for repo-resident emitters)
3. **Stable raw URL** — `https://raw.githubusercontent.com/kvkalidindi/swiss_design_at_deccan/main/skill/assets/templates/document.html` — public, GitHub CDN
4. **Inline copy** — paste the template content directly into the artifact

## Rendering paths

- **For Claude.ai cloud sessions**: fetch the template from the stable raw URL above. Inline the bundled fonts (`https://raw.githubusercontent.com/kvkalidindi/swiss_design_at_deccan/main/skill/assets/fonts.b64.txt`) and the logo (`https://raw.githubusercontent.com/kvkalidindi/swiss_design_at_deccan/main/skill/assets/logo.b64.txt`) as data URIs by replacing the `url(../fonts/...)` and `src=../logo.png` references. The result is a fully self-contained HTML artifact with zero network dependencies.
- **For Claude Code / local Python emitters**: copy the template, run any local templating engine (Jinja2, plain string-replace, etc.), open the result in a browser to print to PDF, or feed to WeasyPrint / wkhtmltopdf for headless rendering.
- **For Word output**: this template is for HTML/PDF. For native `.dotx` / `.docx` use the existing Office templates in `office/templates/deccan.dotx`, which encode the same rules in Word's styles.xml.

## Why a template, not just a spec

The spec describes the rules ("title is 36pt, font-weight 300, Deccan Blue"); the template *enforces* them. When three different cloud sessions are asked to emit a Deccan PDF from the same prose spec, they produce three different documents — different fonts, different metadata schemas, different heading weights — because the spec leaves room for interpretation. The template removes that room. The model fills slots; it does not invent the surface.

## Conformance

The template implements every hard rule in `document-furniture.md`:

- ✅ Self-contained cover with logo + title + subtitle + author + version + date + classification
- ✅ Cover has no header/footer/page number (`@page cover-page` clears them)
- ✅ Every `<h1>` starts on a new page (`page-break-before: always`)
- ✅ Body fills full content width (no `max-w-60ch` restriction)
- ✅ 0.8″ margins → 6.9″/8.5″ = 81.2% live content area
- ✅ End page after explicit page break (`page-break-before: always` on `.end`)
- ✅ Footer page numbers as bare integers (`content: counter(page)`)
- ✅ White page background; stone tints reserved for `.code-inline` / `.code-block` / `.callout` / `table.banded`

Do not modify the structural CSS without re-checking each rule against `document-furniture.md`. Do not add a second accent colour. Do not apply stone tints anywhere outside the four allowed selectors.
