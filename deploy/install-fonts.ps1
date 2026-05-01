#requires -Version 5.1
<#
.SYNOPSIS
    Install IBM Plex Sans and IBM Plex Mono fonts.

.DESCRIPTION
    By default installs to per-user font directory ($env:LOCALAPPDATA\Microsoft\Windows\Fonts)
    so no admin privilege is needed. With -SystemWide, installs to C:\Windows\Fonts
    (requires admin).

    For each TTF, copies the file and registers it in the appropriate fonts registry.
    Idempotent: re-running does not duplicate.

.PARAMETER SystemWide
    Install to C:\Windows\Fonts. Requires admin (PowerShell run as Administrator).

.PARAMETER Uninstall
    Reverse the install: remove the IBM Plex font files and registry entries.
    Honor the same scope as the original install (-SystemWide if applicable).

.EXAMPLE
    .\install-fonts.ps1
    Per-user install of IBM Plex Sans + Mono.
#>
[CmdletBinding()]
param(
    [switch]$SystemWide,
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) { $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }
$ProjectRoot = Resolve-Path (Join-Path $ScriptRoot "..")

# Source font files (Plan 1 deliverable)
$FontSources = @(
    Join-Path $ProjectRoot "fonts\ibm-plex-sans"
    Join-Path $ProjectRoot "fonts\ibm-plex-mono"
)

if ($SystemWide) {
    $FontDir = Join-Path $env:WINDIR "Fonts"
    $RegHive = "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
    if (-not (([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))) {
        throw "-SystemWide requires running PowerShell as Administrator."
    }
} else {
    $FontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
    $RegHive = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
}

if (-not (Test-Path $FontDir)) {
    New-Item -ItemType Directory -Path $FontDir -Force | Out-Null
}
if (-not (Test-Path $RegHive)) {
    New-Item -Path $RegHive -Force | Out-Null
}

function Get-FontDisplayName {
    param([string]$TtfPath)
    # Reads the font's Family + Subfamily for the registry display name.
    # PowerShell's PresentationCore Glyphtypeface gives us this cleanly.
    Add-Type -AssemblyName PresentationCore
    try {
        $uri = New-Object System.Uri($TtfPath)
        $gt = New-Object System.Windows.Media.GlyphTypeface($uri)
        $family = $gt.Win32FamilyNames["en-us"]
        if (-not $family) { $family = ($gt.Win32FamilyNames.Values | Select-Object -First 1) }
        $face = $gt.Win32FaceNames["en-us"]
        if (-not $face) { $face = ($gt.Win32FaceNames.Values | Select-Object -First 1) }
        if ($face -and $face -ne "Regular") {
            return "$family $face (TrueType)"
        } else {
            return "$family (TrueType)"
        }
    } catch {
        $name = [System.IO.Path]::GetFileNameWithoutExtension($TtfPath)
        return "$name (TrueType)"
    }
}

function Install-OneFont {
    param([string]$TtfPath, [string]$FontDir, [string]$RegHive)
    $fileName = Split-Path $TtfPath -Leaf
    $dest = Join-Path $FontDir $fileName
    Copy-Item $TtfPath -Destination $dest -Force
    $displayName = Get-FontDisplayName -TtfPath $dest
    if ($RegHive.StartsWith("HKLM")) {
        $regValue = $fileName
    } else {
        $regValue = $dest
    }
    New-ItemProperty -Path $RegHive -Name $displayName -Value $regValue -PropertyType String -Force | Out-Null
    return $displayName
}

function Uninstall-OneFont {
    param([string]$TtfPath, [string]$FontDir, [string]$RegHive)
    $fileName = Split-Path $TtfPath -Leaf
    $dest = Join-Path $FontDir $fileName
    if (Test-Path $dest) {
        $displayName = Get-FontDisplayName -TtfPath $dest
        Remove-Item $dest -Force
        Remove-ItemProperty -Path $RegHive -Name $displayName -ErrorAction SilentlyContinue
        return $displayName
    }
    return $null
}

if ($Uninstall) {
    Write-Host "Uninstalling Deccan fonts..." -ForegroundColor Yellow
    foreach ($src in $FontSources) {
        if (Test-Path $src) {
            Get-ChildItem $src -Filter *.ttf | ForEach-Object {
                $name = Uninstall-OneFont -TtfPath $_.FullName -FontDir $FontDir -RegHive $RegHive
                if ($name) { Write-Host "  Removed: $name" }
            }
        }
    }
    Write-Host "Uninstall complete." -ForegroundColor Green
    return
}

Write-Host "Installing Deccan fonts..." -ForegroundColor Cyan
Write-Host "  Scope: $(if ($SystemWide) { 'System-wide' } else { 'Per-user' })"
Write-Host "  Destination: $FontDir"
foreach ($src in $FontSources) {
    if (-not (Test-Path $src)) {
        Write-Warning "Missing font source: $src - skipping"
        continue
    }
    Get-ChildItem $src -Filter *.ttf | ForEach-Object {
        $name = Install-OneFont -TtfPath $_.FullName -FontDir $FontDir -RegHive $RegHive
        Write-Host "  Installed: $name"
    }
}
Write-Host ""
Write-Host "Install complete." -ForegroundColor Green
Write-Host "If Office is open, restart it to pick up the new fonts."
