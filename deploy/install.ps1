#requires -Version 5.1
<#
.SYNOPSIS
    Install the full Deccan Chemicals design system on this PC.

.DESCRIPTION
    Installs IBM Plex fonts, Office theme + 3 templates, and configures Office to
    discover the templates via HKCU PersonalTemplates registry keys.

    By default everything is per-user (no admin needed). -SystemWide installs fonts
    machine-wide (admin required); other artifacts remain per-user.

.PARAMETER SystemWide
    Install fonts to C:\Windows\Fonts. Requires admin.

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
    .\install.ps1
    Per-user install of everything.

.EXAMPLE
    .\install.ps1 -DryRun
    Show what would happen.

.EXAMPLE
    .\install.ps1 -Uninstall
    Reverse a previous install.
#>
[CmdletBinding()]
param(
    [switch]$SystemWide,
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

if ($Validate) {
    & (Join-Path $ScriptRoot "validate.ps1")
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

if ($Uninstall) {
    Write-Host "Uninstalling Deccan design system..." -ForegroundColor Yellow

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
        Write-Step "Invoking install-fonts.ps1 -Uninstall $(if ($SystemWide) { '-SystemWide' })"
        if (-not $DryRun) {
            $argsList = @("-Uninstall")
            if ($SystemWide) { $argsList += "-SystemWide" }
            & (Join-Path $ScriptRoot "install-fonts.ps1") @argsList
        }
    }

    Write-Host ""
    Write-Host "Uninstall complete." -ForegroundColor Green
    Write-Host "Restart any open Office apps to refresh."
    return
}

Write-Host "Installing Deccan design system..." -ForegroundColor Cyan
Write-Host "  Scope: $(if ($SystemWide) { 'System-wide' } else { 'Per-user' })"
Write-Host ""

if ($DoFonts) {
    Write-Host "Fonts:"
    Write-Step "Invoking install-fonts.ps1 $(if ($SystemWide) { '-SystemWide' })"
    if (-not $DryRun) {
        $argsList = @()
        if ($SystemWide) { $argsList += "-SystemWide" }
        & (Join-Path $ScriptRoot "install-fonts.ps1") @argsList
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
Write-Host "To reverse: .\install.ps1 -Uninstall"
