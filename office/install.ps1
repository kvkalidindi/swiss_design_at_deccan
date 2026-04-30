#requires -Version 5.1
<#
.SYNOPSIS
    Per-user installer for the Deccan Chemicals Office artifacts.

.DESCRIPTION
    Copies office-theme.thmx and the Word/PowerPoint/Excel templates into the
    current user's Office templates folders, then sets the PersonalTemplates
    registry value for each app so they appear under File > New > Personal.

    Office 2013+ ("Office 365") only shows the Personal tab once that registry
    value is set; copying the files alone is not sufficient.

    All changes are HKCU and per-user. Use -Uninstall to remove.

.PARAMETER Uninstall
    Reverse the install: delete the deccan-* templates and the theme, and
    clear the PersonalTemplates registry value if it points at this folder.

.EXAMPLE
    .\install.ps1
    Installs templates and sets registry keys.

.EXAMPLE
    .\install.ps1 -Uninstall
    Removes templates and clears registry keys.
#>
[CmdletBinding()]
param(
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) { $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }

$TemplatesDir = Join-Path $env:APPDATA "Microsoft\Templates"
$ThemesDir = Join-Path $TemplatesDir "Document Themes"
$Apps = @("Word", "PowerPoint", "Excel")
$OfficeVersion = "16.0"

$Artifacts = @(
    @{ Src = Join-Path $ScriptRoot "office-theme.thmx"; Dst = Join-Path $ThemesDir "office-theme.thmx" }
    @{ Src = Join-Path $ScriptRoot "templates\deccan.dotx"; Dst = Join-Path $TemplatesDir "deccan.dotx" }
    @{ Src = Join-Path $ScriptRoot "templates\deccan.potx"; Dst = Join-Path $TemplatesDir "deccan.potx" }
    @{ Src = Join-Path $ScriptRoot "templates\deccan.xltx"; Dst = Join-Path $TemplatesDir "deccan.xltx" }
)

if ($Uninstall) {
    Write-Host "Removing Deccan Office artifacts and registry settings..." -ForegroundColor Yellow
    foreach ($item in $Artifacts) {
        if (Test-Path $item.Dst) {
            Remove-Item $item.Dst -Force
            Write-Host "  Removed $($item.Dst)"
        }
    }
    foreach ($app in $Apps) {
        $regKey = "HKCU:\Software\Microsoft\Office\$OfficeVersion\$app\Options"
        $current = (Get-ItemProperty -Path $regKey -Name "PersonalTemplates" -ErrorAction SilentlyContinue).PersonalTemplates
        if ($current -eq $TemplatesDir) {
            Remove-ItemProperty -Path $regKey -Name "PersonalTemplates" -ErrorAction SilentlyContinue
            Write-Host "  Cleared PersonalTemplates registry for $app"
        }
    }
    Write-Host "Uninstall complete. Restart any open Office apps to refresh." -ForegroundColor Green
    return
}

Write-Host "Installing Deccan Office artifacts..." -ForegroundColor Cyan

if (-not (Test-Path $ThemesDir)) {
    New-Item -ItemType Directory -Path $ThemesDir -Force | Out-Null
}

foreach ($item in $Artifacts) {
    if (-not (Test-Path $item.Src)) {
        throw "Missing source artifact: $($item.Src). Run scripts/_09_emit_office.py first."
    }
    Copy-Item $item.Src -Destination $item.Dst -Force
    Write-Host "  Copied $($item.Dst)"
}

foreach ($app in $Apps) {
    $regKey = "HKCU:\Software\Microsoft\Office\$OfficeVersion\$app\Options"
    if (-not (Test-Path $regKey)) {
        New-Item -Path $regKey -Force | Out-Null
    }
    New-ItemProperty -Path $regKey -Name "PersonalTemplates" -Value $TemplatesDir -PropertyType ExpandString -Force | Out-Null
    Write-Host "  Set PersonalTemplates for $app -> $TemplatesDir"
}

Write-Host ""
Write-Host "Install complete." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Close any open Word/PowerPoint/Excel windows."
Write-Host "  2. Reopen each app."
Write-Host "  3. File > New > Personal to see deccan.dotx / deccan.potx / deccan.xltx."
Write-Host "  4. For Outlook signature: open templates\signature.htm in a browser, copy, paste into Outlook signature settings."
Write-Host ""
Write-Host "If IBM Plex Sans is not installed, install fonts from project root: fonts/ibm-plex-sans/*.ttf"
Write-Host "(Plan 5 will automate font deployment via Group Policy / Intune.)"
