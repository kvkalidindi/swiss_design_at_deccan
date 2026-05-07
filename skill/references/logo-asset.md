# Logo Asset — Reliable Retrieval

The Deccan corporate logo is the only image that appears in document furniture (cover pages, headers, end pages, signatures). Every artifact emitter — local Python scripts, Claude Code, Claude.ai web/mobile, Office templates — must be able to obtain it deterministically. This reference defines the canonical retrieval order so a transient network failure can never block document generation.

## Source of truth

The single source of truth is **`data/logo.png`** in the [swiss_design_at_deccan](https://github.com/kvkalidindi/swiss_design_at_deccan) repository.

- Format: PNG, 185 × 60 px, 8-bit/color RGBA, non-interlaced
- Size: ~9,358 bytes
- Aspect ratio: ~3.08 : 1 (wider than tall)

Never recolor, recompose, stretch, or rasterize a different version. If the source ever changes, update only `data/logo.png` and re-run `python -m scripts._08_emit_skill` to propagate to all skill assets.

## Retrieval order

When an emitter needs the logo, it tries these sources **in this order** and stops at the first one that succeeds:

1. **Skill-bundled file** — `skill/assets/logo.png` (relative to the skill root). Always present once the skill is loaded; no network required.
2. **Project-local file** — `data/logo.png` in the working tree. Used by local scripts running inside the repo.
3. **Stable raw URL** — `https://raw.githubusercontent.com/kvkalidindi/swiss_design_at_deccan/main/data/logo.png` — public, no auth, served by GitHub's raw CDN. Use only when neither of the above is available, e.g., a Claude.ai conversation that doesn't have the skill bundle materialized as files.
4. **Inline base64 fallback** — `skill/assets/logo.b64.txt` contains the full PNG as a single base64 string (for embedding into HTML/SVG/CSS as a `data:image/png;base64,…` URI). Use when the runtime can't read binary files but can read text.

The stable raw URL is the single network endpoint we commit to keeping live. It is **public**, requires no authentication, and is served from GitHub's CDN — far more reliable than fetching `https://www.deccanchemicals.com/...` directly, which can rate-limit, redirect, or change.

## For Claude.ai (web/mobile)

Claude.ai conversations don't always have the same skill-bundle file access as Claude Code. When generating an HTML/SVG/PDF artifact, prefer the embedded base64 data URI:

```html
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALkAAAA8CAYAAAA60Bs3AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAA…"
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
