# Plan 5: Enterprise Deployment Bundle — Spec + Implementation Plan

**Date:** 2026-04-30
**Status:** Approved (brainstorm 2026-04-30)
**Scope (locked):** Option D — polished single-bundle install with rollback, documented for both individual users and IT fleet rollout.
**Predecessors:** Plans 1-4 shipped (v0.1.0–v0.4.0)

---

## Spec

### Goal
A single `deploy/` bundle that:
- A solo developer can run on their own PC (no admin needed for user-level install)
- An IT team can adapt for fleet rollout via Intune or Group Policy
- Has full rollback support
- Audits its own state via `validate.ps1`

### Best-practice choices made internally (no further questions)
- Font install user-level by default (`%LOCALAPPDATA%\Microsoft\Windows\Fonts\`); `-SystemWide` flag installs to `C:\Windows\Fonts\` (admin required)
- Office templates per-user (consolidates `office/install.ps1` from Plan 3)
- Registry keys HKCU only (no HKLM machine-wide changes)
- Browser font defaults: documented in README, NOT enforced by the install script
- Outlook signature: documented manual paste from `office/templates/signature.htm`
- Rollback: `-Uninstall` reverses everything; `-OnlyFonts` / `-OnlyTemplates` / `-OnlyRegistry` for partial reverses
- `-DryRun` flag: shows what would happen, changes nothing
- `-Validate` flag: invokes validate.ps1 inline

### Deliverables

```
swiss_design_at_deccan/
├── deploy/
│   ├── README.md
│   ├── install.ps1                # top-level orchestrator
│   ├── install-fonts.ps1          # font install (user-level, -SystemWide for admin)
│   ├── uninstall.ps1              # full rollback
│   ├── validate.ps1               # audit current install state
│   ├── intune/
│   │   ├── README.md
│   │   ├── win32app-deccan-design.json
│   │   └── detection.ps1
│   └── gpo/
│       ├── README.md
│       ├── deccan-design.admx
│       └── en-US/deccan-design.adml
└── tests/
    └── test_deploy.py
```

### Out of scope (final)
- AD-driven Outlook signature auto-population
- macOS / Linux deployment
- Mobile devices
- Locales beyond English/Latin

---

## Implementation Plan

### Phase 1: Core PowerShell scripts

**Task 1: `deploy/install-fonts.ps1`**

Installs IBM Plex Sans + Mono TTFs from `fonts/ibm-plex-sans/` and `fonts/ibm-plex-mono/`.
- Default: user-level (`%LOCALAPPDATA%\Microsoft\Windows\Fonts\`)
- `-SystemWide`: system fonts (`C:\Windows\Fonts\`) — requires admin
- Registers each font in registry so Office and other apps see it
- Idempotent

**Task 2: `deploy/install.ps1`**

Top-level orchestrator. Runs (in order):
1. `install-fonts.ps1` (skipped if `-SkipFonts`)
2. Copy Office artifacts (theme + 3 templates) to user templates folder (logic from `office/install.ps1`)
3. Set HKCU `PersonalTemplates` registry for Word/PPT/Excel
4. Print summary

Flags: `-SystemWide`, `-Uninstall`, `-DryRun`, `-Validate`, `-OnlyFonts`, `-OnlyTemplates`, `-OnlyRegistry`

**Task 3: `deploy/uninstall.ps1`**

Reverses everything that `install.ps1` does:
- Remove user fonts (or system fonts if `-SystemWide`)
- Remove Office artifacts
- Clear HKCU `PersonalTemplates` registry keys

**Task 4: `deploy/validate.ps1`**

Returns 0 if all 9 install checks pass, non-zero with detail otherwise. Used both interactively and by Intune detection.

### Phase 2: IT fleet artifacts

**Task 5: `deploy/intune/`**

- `win32app-deccan-design.json`: example metadata for Intune Win32 app deployment (display name, install command, uninstall command, detection script reference)
- `detection.ps1`: thin wrapper around `validate.ps1` returning Intune's expected exit codes (0 = installed, non-zero = not installed)
- `README.md`: end-to-end Intune deployment procedure (build .intunewin via IntuneWinAppUtil, upload, configure detection, assign to groups)

**Task 6: `deploy/gpo/`**

- `deccan-design.admx`: Group Policy admin template defining policies for the bundle
- `en-US/deccan-design.adml`: English language resource file
- `README.md`: GPO deployment procedure (copy ADMX/ADML to PolicyDefinitions, configure via GPMC)

### Phase 3: Tests + docs

**Task 7: `tests/test_deploy.py`**

Validates artifacts without running them:
- All PowerShell files parse as valid PowerShell (use `Get-Content` + AST parse via subprocess to powershell.exe `-NoProfile -Command "[scriptblock]::Create(...)"`)
- ADMX file is valid XML with the expected root element
- ADML file is valid XML
- README files mention all expected sections (smoke check)

**Task 8: `deploy/README.md`**

Comprehensive end-user docs:
- Quick start (single-user install)
- Detailed flag reference
- Validation procedure
- IT fleet section: pointer to `intune/README.md` and `gpo/README.md`
- Troubleshooting (common issues + fixes)

**Task 9: Top-level README + tag v0.5.0**

- Add Plan 5 complete section
- Update Roadmap to mark all 5 plans complete (project finished)
- Annotated tag v0.5.0 with project-completion release notes
- Push

---

## Self-Review

**Spec coverage:** all 8 deliverables map to tasks. PowerShell syntax + XML well-formedness validated by tests. IT-fleet documentation explicitly covers both Intune (modern) and GPO (legacy) paths.

**Placeholder scan:** No "TBD"/"TODO". Best-practice choices are explicit so the implementer doesn't re-raise them.

**Type consistency:** PowerShell flags (`-SystemWide`, `-Uninstall`, `-DryRun`, `-Validate`, `-OnlyFonts`, `-OnlyTemplates`, `-OnlyRegistry`) consistent across `install.ps1` and `uninstall.ps1`. Validate exit codes (0 / non-zero) consistent across `validate.ps1` and Intune `detection.ps1`.

**Scope:** appropriate single subsystem (deployment), ~2 days of work. Single plan.

---

## Implementation strategy

Two subagent dispatches:
1. **Bundle A:** Phase 1 (core PowerShell scripts) + Phase 3 Task 7 (tests) + Phase 3 Task 8 (deploy/README.md). The user-facing install/uninstall/validate experience.
2. **Bundle B:** Phase 2 (Intune + GPO IT-fleet artifacts) + Phase 3 Task 9 (top-level README + tag v0.5.0). The IT-fleet artifacts and final release.

This split keeps each dispatch focused on one technical domain.
