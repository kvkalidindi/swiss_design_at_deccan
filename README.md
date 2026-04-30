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

## Roadmap

- **Plan 2** — modify `zeke/swiss-design-skill` to consume these tokens
- **Plan 3** — Microsoft Office artifacts (.thmx themes, .dotx/.potx/.xltx templates)
- **Plan 4** — Google Workspace artifacts (Slides/Docs templates, admin gallery)
- **Plan 5** — Enterprise deployment (Intune profiles, Group Policy, font installation)
