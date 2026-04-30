# Swiss Design at Deccan

A multi-format design system for Deccan Chemicals, built on the foundation of [zeke/swiss-design-skill](https://github.com/zeke/swiss-design-skill). It extends Swiss design principles beyond web UI to cover Microsoft 365, Google Workspace, print, and brand collateral, with a brand-derived 8-step accent color palette extracted from the corporate logo.

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

## Roadmap

- ~~**Plan 2** — modify `zeke/swiss-design-skill` to consume these tokens~~ **complete (v0.2.0)**
- ~~**Plan 3** — Microsoft Office artifacts (.thmx themes, .dotx/.potx/.xltx templates)~~ **complete (v0.3.0)**
- ~~**Plan 4** — Google Workspace artifacts (Slides/Docs templates, admin gallery)~~ **complete (v0.4.0)**
- **Plan 5** — Enterprise deployment (Intune profiles, Group Policy, font installation)
