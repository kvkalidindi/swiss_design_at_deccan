# Intune Deployment

Deploy the Deccan design system to corporate Windows 11 PCs as an Intune Win32 app.

## Prerequisites

- Microsoft Endpoint Manager / Intune admin access
- IntuneWinAppUtil.exe (download from Microsoft: https://github.com/microsoft/Microsoft-Win32-Content-Prep-Tool)
- A clone of this repository on the packaging machine

## Build the .intunewin package

1. From the project root, copy the deploy directory and the OOXML/font sources into a staging folder. The package needs:
   - `install.ps1` (top-level)
   - `install-fonts.ps1`, `uninstall.ps1`, `validate.ps1`
   - `intune\detection.ps1` (or move it to the staging root)
   - The `office\` folder (theme + templates)
   - The `fonts\` folder (TTFs)
2. Run IntuneWinAppUtil pointing at the staging folder, with `install.ps1` as the source setup file:

   ```cmd
   IntuneWinAppUtil.exe -c "C:\path\to\staging" -s "install.ps1" -o "C:\path\to\output"
   ```

   Output: `install.intunewin` (an opaque encrypted package).

## Upload to Intune

1. In Endpoint Manager admin center: **Apps > All apps > Add > Windows app (Win32)**
2. Upload `install.intunewin`
3. Fill in metadata using `win32app-deccan-design.json` as a reference (display name, publisher, description, version)
4. Program tab:
   - **Install command:** `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1`
   - **Uninstall command:** `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Uninstall`
   - **Install behavior:** User
   - **Device restart behavior:** No specific action
5. Requirements tab: Operating system architecture x64; Minimum operating system Windows 10 1903 (or newer)
6. Detection rules tab: choose **Use a custom detection script** and upload `detection.ps1`
   - Run script as the logged-on credentials
   - Enforce script signature check: No (unless your environment requires signing)
7. Dependencies / Supersedence: leave default
8. Assignments: assign to the user / device groups that should receive the design system. The `win32app-deccan-design.json` shows where to plug in your group IDs

## Verify the deployment

Once a target PC processes the assignment:
- Run `validate.ps1` interactively on the target machine — expect 9/9 pass
- Open Word > File > New > Personal — `deccan` template should appear

## Updating

To roll a new version (e.g., palette changed):
1. Re-run `scripts\_09_emit_office.py` to regenerate the OOXML templates
2. Bump the `version` field in `win32app-deccan-design.json`
3. Rebuild `install.intunewin`
4. Update the existing app in Intune (don't create a duplicate; use **Update** so Intune supersedes the prior version)
