#requires -Version 5.1
<#
.SYNOPSIS
    Install IBM Plex Sans and IBM Plex Mono fonts into the system fonts location
    that Office 365 picks up by default.

.DESCRIPTION
    Default scope is **system-wide** (C:\Windows\Fonts), which is the path
    Office 365 reliably reads from across all user contexts. Requires admin.

    With -PerUser, falls back to %LOCALAPPDATA%\Microsoft\Windows\Fonts (no
    admin needed). Office 2016+ supports per-user fonts on Win10 1809+, but
    in some configurations this path is not picked up by Office until first
    login - system-wide is the more reliable default.

    For each TTF, copies the file with a retry-on-locked-file loop and
    registers it in the appropriate fonts registry. Idempotent.

.PARAMETER PerUser
    Install to %LOCALAPPDATA%\Microsoft\Windows\Fonts (no admin needed).
    Default is system-wide install requiring admin.

.PARAMETER SystemWide
    Deprecated alias for the default behavior. Kept for backwards
    compatibility with prior scripts; ignored if -PerUser is also passed.

.PARAMETER Uninstall
    Reverse the install. Honors the same scope flag (-PerUser) used at
    install time.

.PARAMETER NoPause
    Do not pause for user input at end. Used when this script is called
    from another script (e.g. install.ps1) - the parent handles the pause.

.EXAMPLE
    # System-wide install (the new default; needs Run as Administrator)
    .\install-fonts.ps1

.EXAMPLE
    # Per-user install (no admin needed)
    .\install-fonts.ps1 -PerUser

.EXAMPLE
    # Reverse a system-wide install
    .\install-fonts.ps1 -Uninstall
#>
[CmdletBinding()]
param(
    [switch]$PerUser,
    [switch]$SystemWide,   # deprecated alias; kept for compatibility
    [switch]$Uninstall,
    [switch]$NoPause
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) { $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }
$ProjectRoot = Resolve-Path (Join-Path $ScriptRoot "..")

function Test-IsAdmin {
    $p = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Pause-IfTopLevel {
    # Only pause if this script was launched directly (not called from another
    # script like install.ps1). Heuristic: $NoPause flag covers explicit
    # programmatic calls.
    if ($NoPause) { return }
    if (-not [Environment]::UserInteractive) { return }
    Write-Host ""
    Write-Host "Press Enter to close this window..." -ForegroundColor Cyan
    [void](Read-Host)
}

# Resolve scope. -PerUser wins if both flags passed. Default = system-wide.
$Scope = if ($PerUser) { "PerUser" } else { "SystemWide" }

if ($Scope -eq "SystemWide" -and -not (Test-IsAdmin)) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host " ADMIN RIGHTS REQUIRED" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "This script installs fonts into C:\Windows\Fonts\ where Office 365"
    Write-Host "reliably picks them up. That path requires Administrator privileges."
    Write-Host ""
    Write-Host "Two ways to fix:"
    Write-Host ""
    Write-Host "  1. RECOMMENDED. Right-click PowerShell -> Run as Administrator,"
    Write-Host "     then re-run:    .\install-fonts.ps1"
    Write-Host ""
    Write-Host "  2. Per-user install (no admin needed; less reliable for some"
    Write-Host "     Office configurations):"
    Write-Host "                     .\install-fonts.ps1 -PerUser"
    Write-Host ""
    Pause-IfTopLevel
    exit 1
}

if ($Scope -eq "SystemWide") {
    $FontDir = Join-Path $env:WINDIR "Fonts"
    $RegHive = "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
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

# Source font files (Plan 1 deliverable). Auto-enumerates every directory
# under <project>/fonts/ that contains at least one .ttf, so adding a new
# font family just means dropping its TTFs into a new fonts/<family>/ dir
# without touching this script.
$FontsRoot = Join-Path $ProjectRoot "fonts"
$FontSources = @()
if (Test-Path $FontsRoot) {
    $FontSources = Get-ChildItem $FontsRoot -Directory -ErrorAction SilentlyContinue |
        Where-Object {
            (Get-ChildItem $_.FullName -Filter *.ttf -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0
        } |
        Sort-Object Name |
        ForEach-Object { $_.FullName }
}
if ($FontSources.Count -eq 0) {
    Write-Warning "No font directories with TTFs found under $FontsRoot."
}

function Get-FontDisplayName {
    param([string]$TtfPath)
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

function Copy-WithRetry {
    param([string]$Source, [string]$Destination, [int]$MaxAttempts = 3)
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            Copy-Item $Source -Destination $Destination -Force -ErrorAction Stop
            return $true
        } catch [System.IO.IOException] {
            # File-in-use is the common failure when Office or a font preview
            # has the destination locked. Wait briefly and retry.
            if ($attempt -lt $MaxAttempts) {
                Start-Sleep -Milliseconds 500
                continue
            }
            Write-Warning ("  Could not copy " + (Split-Path $Source -Leaf) + " (file in use). " +
                           "Close Office / font previewers and re-run, or delete the existing " +
                           "file at $Destination manually.")
            return $false
        }
    }
    return $false
}

function Install-OneFont {
    param([string]$TtfPath, [string]$FontDir, [string]$RegHive)
    $fileName = Split-Path $TtfPath -Leaf
    $dest = Join-Path $FontDir $fileName
    if (-not (Copy-WithRetry -Source $TtfPath -Destination $dest)) {
        return $null
    }
    $displayName = Get-FontDisplayName -TtfPath $dest
    if ($RegHive.StartsWith("HKLM")) {
        # System-wide registry stores filename only; Windows resolves against
        # %SystemRoot%\Fonts\.
        $regValue = $fileName
    } else {
        # Per-user registry stores absolute path.
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
        try {
            Remove-Item $dest -Force -ErrorAction Stop
        } catch [System.IO.IOException] {
            Write-Warning "  Could not delete $dest (file in use). Close Office and re-run."
            return $null
        }
        Remove-ItemProperty -Path $RegHive -Name $displayName -ErrorAction SilentlyContinue
        return $displayName
    }
    return $null
}

if ($Uninstall) {
    Write-Host "Uninstalling Deccan fonts..." -ForegroundColor Yellow
    Write-Host "  Scope: $Scope"
    Write-Host "  Source dir: $FontDir"
    foreach ($src in $FontSources) {
        if (-not (Test-Path $src)) { continue }
        $famSlug = Split-Path $src -Leaf
        Write-Host ""
        Write-Host "  Family: $famSlug"
        $famRemoved = 0
        Get-ChildItem $src -Filter *.ttf | ForEach-Object {
            $name = Uninstall-OneFont -TtfPath $_.FullName -FontDir $FontDir -RegHive $RegHive
            if ($name) {
                Write-Host "    Removed: $name"
                $famRemoved++
            }
        }
        if ($famRemoved -eq 0) {
            Write-Host "    (nothing to remove)" -ForegroundColor DarkGray
        }
    }
    Write-Host ""
    Write-Host "Uninstall complete." -ForegroundColor Green
    Write-Host "If Office is open, restart it to fully unload the fonts."
    Pause-IfTopLevel
    return
}

Write-Host "Installing Deccan fonts..." -ForegroundColor Cyan
Write-Host "  Scope: $Scope"
Write-Host "  Destination: $FontDir"
Write-Host "  Families found in repo:" ($FontSources | ForEach-Object { Split-Path $_ -Leaf }) -ForegroundColor DarkGray
$installedCount = 0
$skippedCount = 0
$familyResults = @()
foreach ($src in $FontSources) {
    if (-not (Test-Path $src)) {
        Write-Warning "Missing font source: $src - skipping"
        continue
    }
    $famSlug = Split-Path $src -Leaf
    Write-Host ""
    Write-Host "  Family: $famSlug"
    $famInstalled = 0
    $famSkipped = 0
    Get-ChildItem $src -Filter *.ttf | ForEach-Object {
        $name = Install-OneFont -TtfPath $_.FullName -FontDir $FontDir -RegHive $RegHive
        if ($name) {
            Write-Host "    Installed: $name"
            $installedCount++
            $famInstalled++
        } else {
            $skippedCount++
            $famSkipped++
        }
    }
    $famTotal = $famInstalled + $famSkipped
    $color = if ($famSkipped -eq 0) { "Green" } else { "Yellow" }
    Write-Host ("    Family summary: {0}/{1} files installed" -f $famInstalled, $famTotal) -ForegroundColor $color
    $familyResults += [pscustomobject]@{
        Family    = $famSlug
        Installed = $famInstalled
        Skipped   = $famSkipped
        Total     = $famTotal
    }
}

# Notify Windows that the font collection changed (broadcasts WM_FONTCHANGE)
# so currently-running apps refresh their font lists. Without this, you must
# log out / restart Word for new fonts to appear.
Add-Type -ErrorAction SilentlyContinue @"
using System;
using System.Runtime.InteropServices;
public static class FontNotify {
    [DllImport("gdi32.dll")] public static extern int AddFontResourceW(string lpFilename);
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
    public static readonly IntPtr HWND_BROADCAST = new IntPtr(0xffff);
    public const uint WM_FONTCHANGE = 0x001D;
}
"@
try {
    foreach ($src in $FontSources) {
        if (-not (Test-Path $src)) { continue }
        Get-ChildItem $src -Filter *.ttf | ForEach-Object {
            $dest = Join-Path $FontDir $_.Name
            if (Test-Path $dest) {
                [void][FontNotify]::AddFontResourceW($dest)
            }
        }
    }
    [void][FontNotify]::SendMessage([FontNotify]::HWND_BROADCAST, [FontNotify]::WM_FONTCHANGE, [IntPtr]::Zero, [IntPtr]::Zero)
} catch {
    # Non-fatal: font is still installed; just won't refresh in already-running apps.
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Family-by-family summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
foreach ($r in $familyResults) {
    $marker = if ($r.Skipped -eq 0) { "[OK]   " } else { "[WARN] " }
    $color  = if ($r.Skipped -eq 0) { "Green" } else { "Yellow" }
    $line   = "{0}{1,-20} {2}/{3} files" -f $marker, $r.Family, $r.Installed, $r.Total
    Write-Host $line -ForegroundColor $color
}
Write-Host ""
Write-Host "Install complete: $installedCount installed, $skippedCount skipped (across $($familyResults.Count) families)." -ForegroundColor Green
if ($skippedCount -gt 0) {
    Write-Host ""
    Write-Host "Some files were skipped (most commonly because Office/font-previewer had them locked)." -ForegroundColor Yellow
    Write-Host "Close Word/PowerPoint/Excel and re-run this script if any family shows < full coverage."
}
Write-Host ""
Write-Host "Office windows that were open at install time should be closed and reopened to pick up the new fonts."
Pause-IfTopLevel
