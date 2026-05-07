# Deccan Design System — Deployment Bundle

This directory contains everything needed to install the Deccan Fine Chemicals design system on a Windows PC: IBM Plex fonts, Office theme + 3 templates, and the registry settings that make Office discover them.

## Quick start (default: system-wide fonts)

Open PowerShell **as Administrator**, then:

```powershell
.\install.ps1
```

By default the installer puts fonts into `C:\Windows\Fonts\` — the system path Office 365 reliably reads from. Office templates and registry keys go into your per-user profile (no admin needed for those parts; admin is only needed for the font install).

After it finishes, the script pauses on `"Press Enter to close this window..."` so you can read the final state. Then close and reopen Word / PowerPoint / Excel for them to pick up the new fonts.

## Per-user install (no admin needed)

If you don't have admin rights, or you only want to install fonts for the current user:

```powershell
.\install.ps1 -PerUser
```

This puts fonts into `%LOCALAPPDATA%\Microsoft\Windows\Fonts\` instead. Office 2016+ on Windows 10 1809+ supports per-user fonts, but in some configurations Office doesn't pick them up until you log out and back in. **System-wide is the recommended default.**

## What gets installed (default)

| Component | Path | Scope |
|---|---|---|
| Fonts (IBM Plex Sans + Mono) | `C:\Windows\Fonts\` | System-wide (admin) |
| Office theme | `%APPDATA%\Microsoft\Templates\Document Themes\office-theme.thmx` | Per-user |
| Word/PPT/Excel templates | `%APPDATA%\Microsoft\Templates\deccan.{dotx,potx,xltx}` | Per-user |
| Registry: `PersonalTemplates` | `HKCU:\Software\Microsoft\Office\16.0\<App>\Options` | Per-user |

With `-PerUser`, fonts move to `%LOCALAPPDATA%\Microsoft\Windows\Fonts\` and registered under HKCU. Other paths are unchanged.

## Window stays open at end

All top-level scripts (`install.ps1`, `uninstall.ps1`, `validate.ps1`) pause on a `Press Enter to close this window...` prompt before exiting, so you can read the final report whether the script was launched from a terminal, by double-click, or by Run-with-PowerShell from Explorer. Pass `-NoPause` to disable (used by Intune detection and parent scripts).

## Flags

| Flag | Effect |
|---|---|
| `-PerUser` | Install fonts at user level instead of system-wide. No admin needed. |
| `-Uninstall` | Reverse everything (or only the parts requested by other flags). |
| `-DryRun` | Print what would happen, change nothing. |
| `-Validate` | Audit current state via `validate.ps1`. |
| `-OnlyFonts` | Install/uninstall only fonts. |
| `-OnlyTemplates` | Install/uninstall only Office artifacts. |
| `-OnlyRegistry` | Set/clear only registry keys. |
| `-SystemWide` | (Deprecated alias — system-wide is the default now. Kept for backwards compatibility.) |

Examples:

```powershell
.\install.ps1                          # Default: system-wide fonts (admin)
.\install.ps1 -PerUser                 # User-level fonts (no admin)
.\install.ps1 -DryRun                  # Preview the install
.\install.ps1 -Uninstall               # Reverse a previous install
.\install.ps1 -Uninstall -OnlyFonts    # Remove only the fonts
.\install.ps1 -Uninstall -PerUser      # Reverse a -PerUser install
.\install.ps1 -Validate                # Audit the install
```

## Validation

```powershell
.\validate.ps1
```

Returns exit code 0 if all 9 checks pass. Reports the **scope** (system-wide vs per-user) of each detected font so you can tell where things actually live. Used both interactively and by Intune detection (see `intune/`).

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
| Word renders document with a different font (e.g. Inter) | IBM Plex not actually installed | Re-run `.\install.ps1` (or `-OnlyFonts`). Then close and reopen Word. |
| `.\install.ps1` stops with "ADMIN RIGHTS REQUIRED" | You're not running PowerShell as administrator | Right-click PowerShell → Run as administrator, retry. Or use `-PerUser`. |
| Validate fails on `IBM Plex Sans installed` after a successful install | Office had the font file open during copy → file-locked → silently skipped | Close all Office apps, re-run `.\install.ps1 -OnlyFonts`. The script auto-retries 3 times for in-use files. |
| Window closes before I can read the output | Earlier script revisions auto-closed | Update — current revision pauses with `Press Enter to close...` |

## Regenerating

If Plan 1 palette / fonts evolve, regenerate the source artifacts via the Python pipeline first (`scripts/_09_emit_office.py`, `scripts/_10_emit_gworkspace.py`), then re-run `.\install.ps1` to push the new artifacts onto the local machine.
