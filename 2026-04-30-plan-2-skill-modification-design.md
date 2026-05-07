# Plan 2: Deccan Swiss-Design Skill — Design Spec

**Date:** 2026-04-30
**Owner:** kishore.kalidindi@deccanchemicals.com
**Status:** Approved (brainstorm 2026-04-30)
**Predecessor:** Plan 1 (palette + typography foundation, shipped at v0.1.0)

---

## 1. Background & Goal

Plan 1 produced the brand-derived 8-step accent palette, typography stack, and supporting deliverables (palette.json/css/ase/html/md, fonts/, typography.md). Plan 2 takes the upstream [zeke/swiss-design-skill](https://github.com/zeke/swiss-design-skill) — a Claude Code skill encoding Swiss International Style design principles — and customizes it for Deccan Fine Chemicals so that engineers, designers, and AI agents producing Deccan-branded UIs follow the same system.

The deliverable is a self-contained Claude Code skill at `swiss_design_at_deccan/skill/` that any user can install (copy to `~/.claude/skills/` or reference via plugin manifest) and have AI agents produce Deccan-branded UIs by default.

---

## 2. Philosophical alignment with upstream

The upstream skill's defining rule is **"one accent color per project"** (Swiss design principle 5). It explicitly forbids mixing two accents simultaneously. Our 8-step dual-color palette nominally provides two accent families (blue + green).

**Resolution:** Honor the upstream "one accent" rule.

- **Primary accent:** `#164999` (Deccan deep navy — `blue-500` from Plan 1)
- **Secondary brand mark:** `#71BF4D` (Deccan true green — `green-500` from Plan 1) — used **only** in the corporate logo and explicit sustainability/environmental contexts. Documented as out of scope for default UI.
- **Full 8-step palette:** Available for charts and data visualization via `outputs/palette.json`. Kept architecturally separate from the "one accent" UI rule.

This preserves brand identity (the deep navy IS the corporate identity color) while keeping the design system orthodox.

---

## 3. Repository structure

The skill lives **inside** the existing `swiss_design_at_deccan/` repo at `skill/`. Single repo, single git history, single release cadence.

```
swiss_design_at_deccan/
├── outputs/                   # Plan 1 — palette tokens
├── typography/                # Plan 1 — typography stack
├── fonts/                     # Plan 1 — packaged fonts
├── scripts/                   # palette pipeline + skill emitter
├── skill/                     # ← Plan 2 deliverable
│   ├── SKILL.md
│   └── references/
│       ├── components.md
│       ├── design-system.md
│       ├── tailwind-config.md
│       ├── prompting.md
│       ├── data-viz.md        # NEW
│       └── brand-marks.md     # NEW
└── tests/
    └── test_skill_emitter.py  # NEW
```

Distribution: end-users copy `skill/` to `~/.claude/skills/swiss-design-deccan/` or reference it via plugin manifest. The procedure is documented at the top of `skill/SKILL.md` and in the project README.

---

## 4. File-by-file changes from upstream

| Upstream file | Output | Change summary |
|---|---|---|
| `swiss-design/SKILL.md` | `skill/SKILL.md` | Frontmatter (`name`, `description`, `author`, `version`); body examples re-pointed to Deccan accent. |
| `swiss-design/references/design-system.md` | `skill/references/design-system.md` | Replace 4-option accent table with single Deccan accent. Update CSS custom-properties block to use `#164999` and reference `outputs/palette.css` for the canonical token file. |
| `swiss-design/references/tailwind-config.md` | `skill/references/tailwind-config.md` | All `#C8102E` → `#164999`. Add comment about the secondary green mark and a pointer to `brand-marks.md`. |
| `swiss-design/references/components.md` | `skill/references/components.md` | Inline accent hex codes → `#164999`. |
| `swiss-design/references/prompting.md` | `skill/references/prompting.md` | Update color/example references to use Deccan tokens. |
| (new) | `skill/references/data-viz.md` | Documents how to use the full 8-step palette (blue 100/300/500/700 + green 100/300/500/700) for charts/dashboards. Explicit boundary: data-viz follows different rules than UI chrome. |
| (new) | `skill/references/brand-marks.md` | Documents the secondary green mark with explicit usage rules: logo only, sustainability content only, never as a UI accent in concert with blue. |

### Out of scope (intentionally NOT changed)
- Stone neutral palette (`stone-50` through `stone-950`) — stays as upstream.
- Type scale, spacing, grid system, breakpoints, line heights, letter-spacing.
- The 6 Swiss principles.
- License (MIT, same as upstream).
- The `website/` demo subdirectory (the Deccan corporate website is a separate downstream project, not part of this skill).

---

## 5. Token-emission script

`scripts/_08_emit_skill.py` regenerates `skill/` from a combination of inputs:

1. **`.tmp_swiss/swiss-design/`** — source template (re-clone if needed; gitignored).
2. **`outputs/palette.css`** — canonical Deccan tokens.
3. **`typography/typography.md`** — typography stack (already aligned with upstream — no transformation needed).

The emitter:
- Reads each upstream markdown file.
- Applies a small set of declarative transformations (regex replacements for accent hex codes, frontmatter rewrites for SKILL.md).
- Writes the result to `skill/`.
- Generates the two new reference files (`data-viz.md`, `brand-marks.md`) from templates.

Re-running `_08_emit_skill.py` produces a clean rebuild. This is useful when:
- The Plan 1 palette evolves (re-emit the skill to pick up new hex codes).
- Upstream `swiss-design-skill` releases a material update (re-clone `.tmp_swiss/`, re-emit, hand-merge any changes that don't match our regex transformations).

---

## 6. Testing

`tests/test_skill_emitter.py` validates:
- The emitter runs end-to-end without errors.
- Produced `skill/` contains the 6 expected files.
- `skill/SKILL.md` has valid frontmatter with `name: swiss-design-deccan`.
- No occurrence of `#C8102E` (upstream Swiss Red) or other upstream accents remains in the output.
- Every reference file mentions `#164999` at least once.
- `brand-marks.md` mentions the secondary green `#71BF4D` and its restricted usage.

These are content-validation tests, not behavioral tests of agent output. Behavioral validation (does the skill actually produce good UIs?) requires manual eval and is out of scope for Plan 2.

---

## 7. Installation procedure (documented in skill body)

Two paths for end-users:

### Path A: Copy to user skills directory

```bash
cp -r skill/ ~/.claude/skills/swiss-design-deccan/
```

Claude Code picks it up automatically on next session.

### Path B: Plugin manifest

Add to `~/.claude/plugins/manifest.json`:

```json
{
  "plugins": [
    { "name": "swiss-design-deccan", "path": "/path/to/swiss_design_at_deccan/skill" }
  ]
}
```

Both paths are documented at the top of `skill/SKILL.md`.

---

## 8. Success criteria

1. An engineer who installs `skill/` and asks Claude Code to "style this page with our design system" gets output using `#164999` as the accent, `IBM Plex Sans` as the typeface, and the upstream Swiss layout/grid principles.
2. The skill explicitly forbids the agent from using `#71BF4D` as a UI accent (only in logo / sustainability context per `brand-marks.md`).
3. Re-running `scripts/_08_emit_skill.py` produces an identical `skill/` (idempotent).
4. `pytest` passes the test_skill_emitter validation suite.
5. The skill is installable on a clean Claude Code setup and discoverable in the skills list.

---

## 9. Out of scope

- The `website/` demo from upstream — not adapted; out of scope.
- The Deccan corporate website rebuild — that's a separate downstream project (will live elsewhere).
- Microsoft Office artifacts (Plan 3).
- Google Workspace artifacts (Plan 4).
- Enterprise deployment (Plan 5).
- Behavioral evaluation of agent output quality after installing the skill.
- Bilingual / multi-script typography support.

---

## 10. Open questions (resolved during implementation)

- Exact regex patterns for accent hex replacement (will use a small mapping dict in `_08_emit_skill.py`).
- Whether `prompting.md` contains any accent-color references at all (audit during implementation; the change list above may be smaller in practice).
- Whether the upstream's `darkMode: 'media'` preference should change for Deccan (likely keep as-is — Swiss design works in both modes).

---

## 11. Next step

Invoke the `superpowers:writing-plans` skill to produce the detailed implementation plan that sequences:

1. Audit upstream content for accent references.
2. Write the regeneration script (`_08_emit_skill.py`).
3. Run, generate `skill/`, hand-tweak the two new reference files.
4. Test, commit, document install procedure.
5. Tag v0.2.0.
