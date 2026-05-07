# Swiss Design at Deccan

A multi-format design system for Deccan Fine Chemicals, built on the foundation of [zeke/swiss-design-skill](https://github.com/zeke/swiss-design-skill). It extends Swiss design principles beyond web UI to cover Microsoft 365, Google Workspace, print, and brand collateral, with a brand-derived 8-step accent color palette extracted from the corporate logo.

## Status

**Plan 1 complete (v0.1.0)** — Color palette + typography foundation shipped.

- `outputs/palette.{json,css,ase,html,md}` — 8-step accent palette in 5 formats
- `typography/typography.md` — typography stack documentation
- `typography/substitution-map.json` — canonical font stack (machine-readable)
- `typography/audit-notes.md` — license audit of upstream swiss-design-skill
- `fonts/<family>/` — packaged SIL OFL fonts ready for enterprise deployment

### Plan 1 deliverables (8-step accent palette)

| | 100 (tint) | 300 (light) | 500 (anchor) | 700 (dark) |
|---|---|---|---|---|
| Blue | `#E0E8F5` | `#0EA3DD` | `#164999` | `#0C2956` |
| Green | `#E9EFE6` | `#A1CB8D` | `#71BF4D` | `#4F8D33` |

### Plan 1 deliverables (typography)

Primary: **IBM Plex Sans** (display/body/UI), **IBM Plex Mono** (code).
Fallbacks: Hanken Grotesk, Barlow, Host Grotesk, DM Sans, Fira Code.
All SIL OFL 1.1 — enterprise-deployable without licensing concerns.

**Plan 2 complete (v0.2.0)** — Deccan Swiss-design skill shipped.

- `skill/SKILL.md` + 6 reference files — installable Claude Code skill
- Single accent (`#164999`); secondary green mark restricted to logo / sustainability
- Re-generated from upstream via `scripts/_08_emit_skill.py` (idempotent)

### Installing the skill

**User-level install (Windows PowerShell):**

```powershell
$dest = "$env:USERPROFILE\.claude\skills\swiss-design-deccan"
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Copy-Item -Path skill -Destination $dest -Recurse -Force
```

**User-level install (macOS / Linux):**

```bash
cp -r skill "$HOME/.claude/skills/swiss-design-deccan"
```

Claude Code picks it up automatically on next session.

**Plugin manifest install:** add an entry to `~/.claude/plugins/manifest.json`:

```json
{ "plugins": [
  { "name": "swiss-design-deccan", "path": "/absolute/path/to/swiss_design_at_deccan/skill" }
]}
```

**Plan 3 complete (v0.3.0)** — Microsoft Office artifacts shipped.

- `office/office-theme.thmx` — installable Office theme with 12-slot color scheme
- `office/templates/deccan.{dotx,potx,xltx}` — Word/PowerPoint/Excel templates
- `office/templates/signature.htm` — Outlook email signature with embedded logo
- `office/README.md` — install instructions

See `office/README.md` for per-user install. Plan 5 will automate fleet deployment via Intune/GPO.

**Plan 4 complete (v0.4.0)** — Google Workspace setup shipped.

- `gworkspace/gmail-signature.htm` — Gmail-optimized signature (under 10 KB)
- `gworkspace/README.md` — upload-and-convert setup guide for Slides/Docs/Sheets + Gmail signature install

The Slides/Docs/Sheets templates are reused from `office/templates/` (Google opens OOXML natively).

**Plan 5 complete (v0.5.0)** — Enterprise deployment bundle shipped.

- `deploy/install.ps1` — top-level orchestrator (fonts + Office artifacts + registry); per-user by default, `-SystemWide` for admin, `-Uninstall` / `-DryRun` / `-Validate` flags
- `deploy/install-fonts.ps1` — IBM Plex font installer
- `deploy/uninstall.ps1` — rollback wrapper
- `deploy/validate.ps1` — 9-check audit (fonts + artifacts + registry)
- `deploy/intune/` — Intune Win32 app artifacts (detection script + metadata + README)
- `deploy/gpo/` — Group Policy ADMX/ADML templates + README
- `deploy/README.md` — comprehensive end-user docs

A solo developer runs `.\deploy\install.ps1` and is fully set up. IT teams adapt for fleet rollout via Intune (modern) or Group Policy (legacy).

**Project status: complete.** All 5 plans shipped. Each layer (palette, skill, Office, Workspace, deployment) is independently usable, regenerable, testable.

## Known issues

### Claude.ai is not a deterministic high-fidelity PDF renderer

Documents generated through Claude.ai (web, desktop, mobile) are rendered by whichever PDF pipeline the back-end happens to invoke for that run. We have observed three different renderers across runs of the same document on this project:

| Run | Producer / Creator | Embedded fonts |
|-----|---------------------|----------------|
| `python_and_jupyter_admin_guide.pdf` | Qt 5.15.13 / **wkhtmltopdf 0.12.6** | LiberationSans (regular/bold/italic) + LiberationMono |
| `python_admin_guide_3.pdf` | **Skia/PDF m141** (headless Chromium on Linux) | DejaVu Sans + DejaVu Sans Mono |
| `python_admin_guide_4.pdf` | **Skia/PDF m148** (headless Edge / Chromium on Windows) | IBM Plex Sans subsets (after the v3 template fix) |

This is not unique to Claude.ai — every system that delegates rendering to a third-party (CI runners, ephemeral cloud containers, "open in Word Online") has the same property. The renderer is not part of your contract; only the bytes you hand it are.

#### Why this happens

We don't have authoritative visibility into Anthropic's internal artifact-rendering pipeline. The honest possibilities:

- The Claude.ai web app, desktop app, Claude Code, and any agentic / file-output capability each likely call into different rendering services depending on file type, infrastructure region, and whether the run was interactive vs. tool-driven. There is no public guarantee that "render this HTML to PDF" goes through the same pipeline across runs — only that it produces *a* PDF.
- The pipelines themselves get upgraded out from under users. The Skia/PDF version went `m141` → `m148` between the broken and the regenerated PDF. Behavior shifts even within a single nominally-identical renderer.
- "Generate a PDF" is sometimes done by the model emitting Markdown / HTML and a server-side post-processor doing the conversion (wkhtmltopdf is the cheapest off-the-shelf choice for that), and sometimes by spinning up a headless browser inside a sandbox. Cost, latency, and language all push the choice around.

#### Why network egress to Google Fonts is blocked in the rendering environment

Almost certainly a deliberate security choice, not an oversight. A sandbox that runs untrusted, prompt-influenceable code with outbound HTTP egress is an SSRF and exfiltration vector — the same prompt that says "fetch Google Fonts" can be replaced by an injection that says "fetch attacker.example.com with the contents of the document." The standard mitigation is a default-deny egress policy with a narrow allowlist. Google Fonts is a reasonable allowlist candidate in principle, but it is not on the list today, and even if it were, that just shifts the dependency onto Google's CDN being reachable and the URL being stable. CDNs do disappear (Adobe Typekit's Edge Web Fonts, the GDPR injunction in Germany in 2022 that briefly made `fonts.googleapis.com` legally hazardous to embed in EU pages).

#### How this project mitigates it

Document fidelity in this design system does not depend on the renderer's environment. Every spec-critical resource lives **inside the artifact**:

- IBM Plex Sans (variable, weights 100–700) and IBM Plex Mono (regular + bold) are inlined as base64 WOFF2 data URIs in `@font-face src:` (`skill/assets/templates/document.html`). `font-display: block` forces the renderer to wait for the data-URI decode rather than painting a fallback.
- The corporate logo is inlined as a base64 PNG data URI in the cover and end-page `<img>` tags.
- No `@import`, no CDN URLs, no relative `../fonts/` paths, no system-font enumeration.
- `scripts/verify_pdf_fonts.py` asserts post-render that `IBMPlexSans` is in the embedded font dictionary and that no DejaVu / Liberation / Nimbus / FreeSans fallback families are present. Run it on every produced PDF.

#### Operational guidance

Do not position Claude.ai as a high-fidelity print-production endpoint. Position it as a *content* tool, and route final-fidelity production through a renderer you control:

- **Native Office formats**: Office on Windows with the deccan `.dotx` / `.potx` / `.xltx` templates and the bundled fonts installed via `deploy/install.ps1`.
- **HTML / PDF**: a pinned Playwright + Chromium build, a reproducible Docker image with WeasyPrint, or an explicit `msedge --headless=new --print-to-pdf` invocation against the v3 template.

Use the same self-contained template in both paths and the output is byte-identical regardless of whether Claude.ai, Claude Code, or a teammate's laptop produced it.

## Roadmap

- ~~**Plan 2** — modify `zeke/swiss-design-skill` to consume these tokens~~ **complete (v0.2.0)**
- ~~**Plan 3** — Microsoft Office artifacts (.thmx themes, .dotx/.potx/.xltx templates)~~ **complete (v0.3.0)**
- ~~**Plan 4** — Google Workspace artifacts (Slides/Docs templates, admin gallery)~~ **complete (v0.4.0)**
- ~~**Plan 5** — Enterprise deployment (Intune profiles, Group Policy, font installation)~~ **complete (v0.5.0)**

## Project complete

All five plans shipped. The design system is now end-to-end: from logo extraction through enterprise-deployable artifacts.

Future evolution paths (not on the original roadmap):
- Native Google Workspace API generation (option B from Plan 4 brainstorm) if conversion fidelity is insufficient
- True font embedding inside Office templates (requires deep OOXML manipulation; deferred from Plan 3)
- Status-indicator color palette (success/warning/info/error) — explicitly out of the original 8-step accent scope
