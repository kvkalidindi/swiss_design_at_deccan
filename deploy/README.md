# Deccan Design System — Deployment Bundle

This directory contains everything needed to install the Deccan Chemicals design system on a Windows PC: IBM Plex fonts, Office theme + 3 templates, and the registry settings that make Office discover them.

## Quick start (single user)

```powershell
.\install.ps1
```

By default this is a **per-user, no-admin install**. After it finishes, close and reopen Word/PowerPoint/Excel to pick up the changes.

## What gets installed

- **Fonts:** IBM Plex Sans, IBM Plex Mono → `%LOCALAPPDATA%\Microsoft\Windows\Fonts\`
- **Office theme:** `office-theme.thmx` → `%APPDATA%\Microsoft\Templates\Document Themes\`
- **Office templates:** `deccan.dotx`, `deccan.potx`, `deccan.xltx` → `%APPDATA%\Microsoft\Templates\`
- **Registry:** Sets HKCU `PersonalTemplates` for Word, PowerPoint, Excel so the Personal tab appears in `File > New`

## Flags

| Flag | Effect |
|---|---|
| `-SystemWide` | Install fonts to `C:\Windows\Fonts` (machine-wide). Requires admin. Other artifacts still per-user. |
| `-Uninstall` | Reverse everything (or only the parts requested by other flags). |
| `-DryRun` | Print what would happen, change nothing. |
| `-Validate` | Audit current state via `validate.ps1`. |
| `-OnlyFonts` | Install/uninstall only fonts. |
| `-OnlyTemplates` | Install/uninstall only Office artifacts. |
| `-OnlyRegistry` | Set/clear only registry keys. |

Examples:

```powershell
.\install.ps1 -DryRun                  # Preview the install
.\install.ps1 -SystemWide              # Install fonts machine-wide (admin)
.\install.ps1 -Uninstall               # Reverse a previous install
.\install.ps1 -Uninstall -OnlyFonts    # Remove only the fonts
.\install.ps1 -Validate                # Audit the install
```

## Validation

```powershell
.\validate.ps1
```

Returns exit code 0 if all 9 checks pass, non-zero otherwise. Useful interactively and as the basis for Intune detection (see `intune/`).

## Email signatures

The install script does NOT touch Outlook or Gmail signatures (they require manual paste).

- **Outlook:** open `..\office\templates\signature.htm` in a browser, copy, paste into Outlook signature settings.
- **Gmail:** open `..\gworkspace\gmail-signature.html` in a browser, copy, paste into Gmail signature settings.

## Browser default fonts (IT only)

The install script does not override browser font preferences. To set Chrome / Edge defaults to IBM Plex Sans for an entire fleet, push the appropriate Group Policy. See `gpo/README.md` for an example template.

## IT fleet rollout

Two paths documented:

- **Intune:** see `intune/README.md`. Wraps `install.ps1` as a Win32 app with `validate.ps1` as the detection script.
- **Group Policy:** see `gpo/README.md`. Provides ADMX/ADML templates for managed deployment.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `File > New > Personal` is missing | Office cached the absence of the registry key | Close ALL Office apps, then reopen them. |
| Templates render with wrong font | IBM Plex not installed on this machine | Re-run `.\install.ps1` (or `-OnlyFonts`). |
| `install.ps1 -SystemWide` fails | Not running as Administrator | Right-click PowerShell → Run as administrator, retry. |
| Validate fails for `IBM Plex Sans installed` | Font detection couldn't read the family name | Re-run `.\install-fonts.ps1` to ensure the registry entry was created with the right display name. |

## Regenerating

If Plan 1 palette / fonts evolve, regenerate the source artifacts via the Python pipeline first (`scripts/_09_emit_office.py`, `scripts/_10_emit_gworkspace.py`), then re-run `.\install.ps1` to push the new artifacts onto the local machine.
