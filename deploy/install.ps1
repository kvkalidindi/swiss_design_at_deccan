#requires -Version 5.1
<#
.SYNOPSIS
    Install the full Deccan Chemicals design system on this PC.

.DESCRIPTION
    Installs IBM Plex fonts, the Office theme + 3 templates, and the HKCU
    PersonalTemplates registry keys that make Office discover them.

    Default scope is **system-wide** for fonts (C:\Windows\Fonts), which is
    where Office 365 reliably picks them up. Requires Administrator. Use
    -PerUser to install fonts at user level instead (no admin needed, less
    reliable for some Office configurations).

    Office templates and registry keys are always per-user (HKCU + %APPDATA%);
    they don't need admin.

.PARAMETER PerUser
    Install fonts at user level (%LOCALAPPDATA%\Microsoft\Windows\Fonts).
    No admin required. Default behavior installs fonts to C:\Windows\Fonts.

.PARAMETER SystemWide
    Deprecated: this is now the default. Kept for backwards compatibility.

.PARAMETER Uninstall
    Reverse everything: remove fonts, Office artifacts, and registry keys.

.PARAMETER DryRun
    Print what would happen without making any changes.

.PARAMETER Validate
    Run validate.ps1 against the current state.

.PARAMETER OnlyFonts
    Only install/uninstall fonts; skip Office artifacts and registry.

.PARAMETER OnlyTemplates
    Only copy/remove Office artifacts; skip fonts and registry.

.PARAMETER OnlyRegistry
    Only set/clear registry keys; skip fonts and Office artifacts.

.EXAMPLE
    # Default install: system-wide fonts + per-user templates + per-user registry.
    # Run from an elevated PowerShell.
    .\install.ps1

.EXAMPLE
    # Install fonts at user level (no admin needed)
    .\install.ps1 -PerUser

.EXAMPLE
    .\install.ps1 -DryRun
    # Show what would happen, change nothing.

.EXAMPLE
    .\install.ps1 -Uninstall
    # Reverse a previous install.
#>
[CmdletBinding()]
param(
    [switch]$PerUser,
    [switch]$SystemWide,    # deprecated alias; kept for compatibility
    [switch]$Uninstall,
    [switch]$DryRun,
    [switch]$Validate,
    [switch]$OnlyFonts,
    [switch]$OnlyTemplates,
    [switch]$OnlyRegistry
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) { $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }
$ProjectRoot = Resolve-Path (Join-Path $ScriptRoot "..")

function Pause-Before-Exit {
    if (-not [Environment]::UserInteractive) { return }
    Write-Host ""
    Write-Host "Press Enter to close this window..." -ForegroundColor Cyan
    [void](Read-Host)
}

if ($Validate) {
    & (Join-Path $ScriptRoot "validate.ps1") -NoPause
    Pause-Before-Exit
    return
}

$DoFonts = -not ($OnlyTemplates -or $OnlyRegistry)
$DoTemplates = -not ($OnlyFonts -or $OnlyRegistry)
$DoRegistry = -not ($OnlyFonts -or $OnlyTemplates)
if ($OnlyFonts) { $DoFonts = $true; $DoTemplates = $false; $DoRegistry = $false }
if ($OnlyTemplates) { $DoTemplates = $true; $DoFonts = $false; $DoRegistry = $false }
if ($OnlyRegistry) { $DoRegistry = $true; $DoFonts = $false; $DoTemplates = $false }

$TemplatesDir = Join-Path $env:APPDATA "Microsoft\Templates"
$ThemesDir = Join-Path $TemplatesDir "Document Themes"
$Apps = @("Word", "PowerPoint", "Excel")
$OfficeVersion = "16.0"

$Artifacts = @(
    @{ Src = Join-Path $ProjectRoot "office\office-theme.thmx"; Dst = Join-Path $ThemesDir "office-theme.thmx" }
    @{ Src = Join-Path $ProjectRoot "office\templates\deccan.dotx"; Dst = Join-Path $TemplatesDir "deccan.dotx" }
    @{ Src = Join-Path $ProjectRoot "office\templates\deccan.potx"; Dst = Join-Path $TemplatesDir "deccan.potx" }
    @{ Src = Join-Path $ProjectRoot "office\templates\deccan.xltx"; Dst = Join-Path $TemplatesDir "deccan.xltx" }
)

function Write-Step {
    param([string]$Message)
    if ($DryRun) {
        Write-Host "  [DRY-RUN] $Message" -ForegroundColor DarkYellow
    } else {
        Write-Host "  $Message"
    }
}

$FontScopeLabel = if ($PerUser) { "Per-user" } else { "System-wide (C:\Windows\Fonts)" }

if ($Uninstall) {
    Write-Host "Uninstalling Deccan design system..." -ForegroundColor Yellow
    Write-Host "  Font scope being removed: $FontScopeLabel"

    if ($DoTemplates) {
        Write-Host "Templates:"
        foreach ($item in $Artifacts) {
            if (Test-Path $item.Dst) {
                Write-Step "Removing $($item.Dst)"
                if (-not $DryRun) { Remove-Item $item.Dst -Force }
            }
        }
    }

    if ($DoRegistry) {
        Write-Host "Registry:"
        foreach ($app in $Apps) {
            $regKey = "HKCU:\Software\Microsoft\Office\$OfficeVersion\$app\Options"
            $current = (Get-ItemProperty -Path $regKey -Name "PersonalTemplates" -ErrorAction SilentlyContinue).PersonalTemplates
            if ($current -eq $TemplatesDir) {
                Write-Step "Clearing PersonalTemplates for $app"
                if (-not $DryRun) {
                    Remove-ItemProperty -Path $regKey -Name "PersonalTemplates" -ErrorAction SilentlyContinue
                }
            }
        }
    }

    if ($DoFonts) {
        Write-Host "Fonts:"
        Write-Step "Invoking install-fonts.ps1 -Uninstall ($FontScopeLabel)"
        if (-not $DryRun) {
            $argsList = @("-Uninstall", "-NoPause")
            if ($PerUser) { $argsList += "-PerUser" }
            & (Join-Path $ScriptRoot "install-fonts.ps1") @argsList
        }
    }

    Write-Host ""
    Write-Host "Uninstall complete." -ForegroundColor Green
    Write-Host "Restart any open Office apps to refresh."
    Pause-Before-Exit
    return
}

Write-Host "Installing Deccan design system..." -ForegroundColor Cyan
Write-Host "  Font scope: $FontScopeLabel"
Write-Host ""

if ($DoFonts) {
    Write-Host "Fonts:"
    Write-Step "Invoking install-fonts.ps1 ($FontScopeLabel)"
    if (-not $DryRun) {
        $argsList = @("-NoPause")
        if ($PerUser) { $argsList += "-PerUser" }
        & (Join-Path $ScriptRoot "install-fonts.ps1") @argsList
        if ($LASTEXITCODE -ne 0) {
            # install-fonts emitted its own admin/elevation guidance; stop here.
            Write-Host ""
            Write-Host "Font install did not succeed. Stopping." -ForegroundColor Red
            Pause-Before-Exit
            exit $LASTEXITCODE
        }
    }
}

if ($DoTemplates) {
    Write-Host "Templates:"
    if (-not $DryRun) {
        if (-not (Test-Path $ThemesDir)) {
            New-Item -ItemType Directory -Path $ThemesDir -Force | Out-Null
        }
    }
    foreach ($item in $Artifacts) {
        if (-not (Test-Path $item.Src)) {
            throw "Missing source artifact: $($item.Src). Run scripts/_09_emit_office.py first."
        }
        Write-Step "Copy $($item.Src) -> $($item.Dst)"
        if (-not $DryRun) { Copy-Item $item.Src -Destination $item.Dst -Force }
    }
}

if ($DoRegistry) {
    Write-Host "Registry:"
    foreach ($app in $Apps) {
        $regKey = "HKCU:\Software\Microsoft\Office\$OfficeVersion\$app\Options"
        Write-Step "Set $app PersonalTemplates -> $TemplatesDir"
        if (-not $DryRun) {
            if (-not (Test-Path $regKey)) {
                New-Item -Path $regKey -Force | Out-Null
            }
            New-ItemProperty -Path $regKey -Name "PersonalTemplates" -Value $TemplatesDir -PropertyType ExpandString -Force | Out-Null
        }
    }
}

Write-Host ""
Write-Host "Install complete." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Close and reopen Word, PowerPoint, Excel."
Write-Host "  2. File > New > Personal to use Deccan templates."
Write-Host "  3. For Outlook signature: open office\templates\signature.htm in browser, copy, paste into Outlook signature settings."
Write-Host "  4. For Gmail signature: open gworkspace\gmail-signature.html in browser, copy, paste into Gmail signature settings."
Write-Host ""
Write-Host "To audit the install: .\install.ps1 -Validate"
Write-Host "To reverse:           .\install.ps1 -Uninstall"
Pause-Before-Exit
