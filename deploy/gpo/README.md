# Group Policy Deployment

Deploy the Deccan design system via Group Policy in Active Directory environments where Intune isn't available.

## What's here

- `deccan-design.admx` — Group Policy admin template. Defines policies for the HKCU `PersonalTemplates` registry values for Word, PowerPoint, Excel.
- `en-US/deccan-design.adml` — English language resource file for the ADMX.

The ADMX/ADML pair only handles the **registry portion** of the install. Font deployment and template-file deployment use other GPO mechanisms (described below).

## Install the ADMX/ADML to your domain

Domain Controller (or Group Policy Central Store):

```cmd
copy deccan-design.admx \\domain\sysvol\domain\Policies\PolicyDefinitions\
copy en-US\deccan-design.adml \\domain\sysvol\domain\Policies\PolicyDefinitions\en-US\
```

Open Group Policy Management (GPMC) on a Domain Controller. The new policies appear under:

**User Configuration > Policies > Administrative Templates > Deccan Design System**

Configure each policy to set its `PersonalTemplates` value to `%APPDATA%\Microsoft\Templates` (or wherever you've deployed the template files).

## Font deployment via GPO

Use Group Policy Preferences:

**User Configuration > Preferences > Windows Settings > Files**

Add a Files preference for each TTF in `fonts\ibm-plex-sans\` and `fonts\ibm-plex-mono\`:

- Source: `\\fileserver\fonts\IBMPlexSans-Regular.ttf` (UNC to a fileshare hosting the TTFs)
- Destination: `%LOCALAPPDATA%\Microsoft\Windows\Fonts\IBMPlexSans-Regular.ttf`
- Action: Replace

Pair this with a registry preference adding the font's display name to:

`HKCU\Software\Microsoft\Windows NT\CurrentVersion\Fonts`

(For machine-wide installs, target `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Fonts` and `C:\Windows\Fonts\` instead — requires a Computer-scope GPO that runs as SYSTEM.)

## Office artifacts (theme + templates)

Use Group Policy Preferences > Files (similar to fonts) to copy:

- `office-theme.thmx` to `%APPDATA%\Microsoft\Templates\Document Themes\office-theme.thmx`
- `deccan.dotx` to `%APPDATA%\Microsoft\Templates\deccan.dotx`
- `deccan.potx` to `%APPDATA%\Microsoft\Templates\deccan.potx`
- `deccan.xltx` to `%APPDATA%\Microsoft\Templates\deccan.xltx`

Source UNC paths point at a fileshare hosting the deployment bundle (the project root or a copy thereof).

## Browser default font (optional)

To force Chrome / Edge to use IBM Plex Sans as default:

- Microsoft Edge admin template: install the Edge ADMX, then configure **User Configuration > Edge > Standard fonts** with `IBM Plex Sans` for sans-serif.
- Chrome: equivalent path with the Chrome ADMX.

These templates are not bundled here; download from Microsoft / Google directly.

## Validation

After GPO applies (login or `gpupdate /force`), run on a target machine:

```powershell
.\validate.ps1
```

Expect 9/9 pass. If anything fails, check the corresponding GPO on the Domain Controller.

## Why not just Intune?

Use this path if your environment is on-prem Active Directory without Intune licensing. For modern hybrid / cloud-managed environments, prefer `intune\` — it bundles everything as a single Win32 app and avoids juggling separate GPO mechanisms for files, registry, and detection.
