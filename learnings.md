# Learnings: producing high-fidelity documents across Claude surfaces

This file captures principles for any design system or Claude skill that
emits print-fidelity artifacts (PDFs, slide decks, branded HTML) for users
who work across multiple Claude surfaces — claude.ai web/desktop/mobile,
Claude Code on a local workstation, and downstream tools that consume the
emitted templates (Word, browser print, Playwright, WeasyPrint).

The principles are deliberately non-project-specific. They are guiding
rails for *any* future skill that targets corporate document fidelity —
not just the design system that produced them. They are ordered from
most load-bearing (the structural choices) down to implementation details
that matter only after the load-bearing decisions are right.

---

## Foundational principles

### 1. Self-contained artifacts are the only durable answer

Inline every spec-critical resource as a base64 data URI inside the HTML
that the renderer prints: WOFF2 font binaries in `@font-face src:`, raster
logos in `<img src="data:image/png;base64,…">`, vector marks in inline
`<svg>`. Once everything sits inside the file, the renderer's environment
— network, filesystem layout, system-installed fonts — is irrelevant.
This is the structural fix. Every other principle in this document is
either a consequence of it or a workaround for skills that haven't done
it yet.

### 2. Sandboxed rendering environments have no network egress

The headless renderer that Claude.ai uses to produce PDFs runs in a
sandbox with default-deny outbound network policy. This is a deliberate
SSRF / exfiltration mitigation, not an oversight. Anything in your CSS
or HTML that requires fetching at print time — `@import url(https://…)`,
`<link rel="stylesheet" href="https://…">`, external `<img src="https://…">`,
external icon fonts — silently produces an empty resource. Assume zero
egress. Always.

### 3. Silent fallback is the default failure mode

When a font resource fails to load, browsers do not warn — they walk the
CSS family list to its terminus and resolve `sans-serif` / `monospace`
through the host's font-config. On Linux that is DejaVu Sans; on a Red
Hat / Fedora image it is Liberation Sans. The PDF renders cleanly, the
process exits 0, and the layout looks roughly right at a glance. The
artifact is non-compliant and indistinguishable from a successful run
without inspection. Never trust "the PDF was produced" as evidence of
correctness.

### 4. The renderer is not part of your contract

Across Claude surfaces, a single nominally-identical request — "render
this HTML to PDF" — has been observed to dispatch to wkhtmltopdf 0.12.6
/ Qt, to headless Chromium / Skia on Linux, and to headless Chromium /
Skia on Windows, in three runs of the same document. The renderer
changes by surface, by region, by interactive-vs-tool path, and by
silent in-place upgrades to the rendering service. Treat the renderer
as an unknown, substitutable downstream consumer. Only the bytes you
hand it are part of the contract.

### 5. Three render surfaces, three failure modes — none of them share a fix

| Surface | Resource source | Dominant failure mode | Mitigation |
|---|---|---|---|
| Office on Windows (Word/Excel/PowerPoint) | OS-installed font files | Font not installed → silent substitution by the host's nearest match. Office never warns. | Install required fonts via MSI/policy + set `embedTrueTypeFonts=1` in OOXML so generated `.docx` carries subsets to recipients. |
| Claude.ai web / desktop / mobile | Sandbox host | No network egress, no domain-relevant fonts pre-installed, non-deterministic renderer. | Inline every spec-critical resource as a base64 data URI inside the artifact. |
| Claude Code on a workstation | Either local renderer + system fonts, or a vendored headless browser | Inherits whichever path the user invokes; OS path varies by OS. | Same data-URI artifact as Claude.ai, plus a pinned Playwright/Chromium adapter so the renderer is part of the toolchain. |

A fix that works for one surface does not generalize. The artifact
strategy (data URIs) is the only one that crosses all three.

### 6. Verify post-render, not just pre-render

Static checks on the source HTML (presence of `data:font/woff2;base64,…`,
absence of `@import`, absence of relative `../fonts/` paths) prove what
was *handed* to the renderer. They do not prove what the renderer
*embedded*. Always follow up with a post-render check that greps the
rendered PDF's font dictionary for the required families and asserts
the absence of the fallback families that signal silent substitution
(DejaVu*, Liberation*, FreeSans, FreeMono, Nimbus*). The renderer's
exit code is not sufficient evidence of correctness.

### 7. Position Claude.ai as a content tool, not a production endpoint

For high-fidelity print production, do not rely on the Claude.ai
rendering pipeline as the final-mile. Use Claude.ai to draft and
iterate on content, then route the final artifact through a renderer
the team controls — Office on Windows for native formats, a pinned
Playwright + Chromium build (or a reproducible Docker image with
WeasyPrint) for HTML/PDF. Use the same self-contained template in
both paths and the output is byte-identical regardless of which
surface produced the file.

---

## Mental models

### 8. The model and the renderer are different processes

What the language model "knows" about a font, a layout, or a brand spec
is irrelevant to what the print process can resolve. The model emits
HTML; the renderer prints what is in that HTML. If the HTML does not
carry the bytes the renderer needs, the model's knowledge of the spec
does not save the output. Treat the renderer as a separate, untrusted
consumer that has only the bytes you hand it.

### 9. Don't trust CDNs as a runtime dependency, even reputable ones

`fonts.googleapis.com` is reputable, well-known, and reliable. It is also
the wrong place to source fonts at print time:

- Sandboxes block egress (see Principle 2).
- Corporate egress proxies block or rewrite requests to third-party CDNs.
- Regulatory action (the 2022 German GDPR injunction made
  `fonts.googleapis.com` legally hazardous to embed in EU pages overnight).
- CDNs are deprecated and disappear (Adobe Typekit's Edge Web Fonts).
- The CDN's URL scheme changes (Google Fonts v1 → v2, breaking some
  clients).

Use CDNs at *development* time to discover which font cuts you need.
Bake the resulting binaries into the artifact for *production*.

### 10. Office and HTML/PDF are not interchangeable production paths

Native Office formats (`.docx`, `.pptx`, `.xlsx`) carry their own font,
style, and embedding rules independent of the HTML/PDF path. Office
respects `embedTrueTypeFonts` in the OOXML; HTML respects `@font-face`.
A generated `.docx` opened on a recipient machine without the fonts
installed silently substitutes — there is no `font-display: block`
equivalent in Word. Always render Office documents on a host that has
the required fonts installed and embedded in the file at save time.

### 11. Build the verification step into the skill, not the user's workflow

A user who has to remember to run a separate verifier will skip it.
Make verification a step the skill emits as part of its own recipe:
"after rendering, run the font verifier; if it fails, the artifact is
not ready to ship." Failure should be loud and machine-readable, not a
visual judgment call.

---

## Specific gotchas

### 12. Relative URLs in templates are a trap

`url('../fonts/X.woff2')` only resolves if the file currently being
parsed lives at the path relative to which `..` was authored. The moment
the template is copied to a temp directory, inlined into a different
file, or moved next to the body content, the path resolves to nothing
and the `@font-face` fails silently. Either inline the bytes (preferred)
or substitute absolute `file://` paths before invoking the renderer.

### 13. `font-display: swap` is the wrong default for print

`swap` tells the renderer to begin layout with a fallback face and swap
to the requested face when it loads. In screen rendering this is a
performance feature. In headless print, the swap can complete *after*
paint, freezing the fallback face into the PDF even though the requested
face would have loaded a millisecond later. Use `font-display: block`
for print stylesheets — the renderer waits for the face to decode before
painting.

### 14. Variable-axis fonts need both format hints

Declare `format('woff2-variations'), format('woff2')` in `@font-face src:`
in that order. Renderers that understand the variable axis pick the
first; renderers that don't fall through to the second and pick a static
weight from the same blob. Without the second hint, non-variable-aware
renderers ignore the font and fall back silently.

### 15. Different renderers subset fonts differently

`wkhtmltopdf` eagerly embeds every font family declared in CSS, even
families no glyph was rendered with. Chromium lazily subsets — it
embeds a family only if a glyph was actually painted in it. The
practical consequence: a doc with no `<strong>` runs gets bold cuts
from `wkhtmltopdf` and not from Chromium. This means the *expected*
font dictionary varies by renderer; verifiers must distinguish
"missing because not used" from "missing because the renderer fell
back."

### 16. Identify the renderer from the PDF, not from assumptions

PDF metadata exposes the renderer pipeline:

- `/Producer (wkhtmltopdf 0.12.6)` and `/Producer (Qt 5.x)` together →
  wkhtmltopdf.
- `/Producer (Skia/PDF mNNN)` and `/Creator (Mozilla/5.0 …)` → headless
  Chromium / Edge. The OS string discloses Linux vs Windows.
- `/Producer (WeasyPrint)` → WeasyPrint.

Read these strings before debugging font issues. They are the cheapest
way to triage which path produced an artifact and which mitigation
applies. Renderer drift between runs is observable here.

### 17. Hash the binary payload to catch silent corruption

A base64-encoded font that has been re-saved with the wrong line endings,
the wrong file order, or a stray BOM injected by a Windows editor parses
as valid CSS but decodes to zero glyphs. The renderer falls back. Ship
the binary payload alongside a sidecar `sha256` of the original bytes,
and have the emitter refuse to render if the hash does not match.

### 18. Template substitution must not collide with prose

Placeholder tokens (`{{TITLE}}`, `{{BODY_HTML}}`, `{{FONTS_CSS}}`) get
duplicated wherever they appear, including inside HTML comments that
*describe* the slot. Never reference a slot's literal token in
commentary; spell it as plain prose ("the FONTS_CSS slot") or wrap it
differently — otherwise the substitution multiplies the payload across
every comment that mentions the slot.
