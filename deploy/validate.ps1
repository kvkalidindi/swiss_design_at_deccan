#requires -Version 5.1
<#
.SYNOPSIS
    Audit the Deccan design system install state on this PC.

.DESCRIPTION
    Checks fonts, Office artifacts, and registry. Returns exit code 0 if all 9
    checks pass, non-zero otherwise. Used both interactively and by Intune
    detection scripts.

    Reports the SCOPE of each font (system-wide C:\Windows\Fonts or per-user
    %LOCALAPPDATA%\Microsoft\Windows\Fonts) so you can tell where the font is
    actually installed.

.PARAMETER NoPause
    Do not pause for user input at end. Used when this script is called from
    install.ps1 -Validate or from an Intune detection harness.

.EXAMPLE
    .\validate.ps1
    Run audit and print pass/fail report. Pauses at end so the window stays
    open when launched via double-click or Run-with-PowerShell.
#>
[CmdletBinding()]
param(
    [switch]$NoPause
)

$ErrorActionPreference = "Stop"

$UserFontsDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$SysFontsDir = Join-Path $env:WINDIR "Fonts"
$TemplatesDir = Join-Path $env:APPDATA "Microsoft\Templates"
$ThemesDir = Join-Path $TemplatesDir "Document Themes"
$Apps = @("Word", "PowerPoint", "Excel")
$OfficeVersion = "16.0"

$Checks = @()

function Add-Check {
    param([string]$Name, [bool]$Pass, [string]$Detail)
    $script:Checks += [pscustomobject]@{
        Name = $Name
        Pass = $Pass
        Detail = $Detail
    }
}

function Pause-Before-Exit {
    if ($NoPause) { return }
    if (-not [Environment]::UserInteractive) { return }
    Write-Host ""
    Write-Host "Press Enter to close this window..." -ForegroundColor Cyan
    [void](Read-Host)
}

# fonts: report which directory the family lives in
Add-Type -AssemblyName PresentationCore -ErrorAction SilentlyContinue
function Get-FontFamilyLocation {
    param(
        [string]$FamilyName,
        [string]$FilenameHint = ""   # e.g. "DMSans" - matched if GlyphTypeface fails
    )
    foreach ($dir in @($SysFontsDir, $UserFontsDir)) {
        if (-not (Test-Path $dir)) { continue }
        $hit = Get-ChildItem $dir -Filter *.ttf -ErrorAction SilentlyContinue | Where-Object {
            $matched = $false
            try {
                $uri = New-Object System.Uri($_.FullName)
                $gt = New-Object System.Windows.Media.GlyphTypeface($uri)
                $fam = $gt.Win32FamilyNames["en-us"]
                if ($fam -eq $FamilyName) { $matched = $true }
            } catch {
                # GlyphTypeface throws on some variable fonts (DM Sans etc.).
                # Fall through to the filename hint match below.
            }
            if (-not $matched -and $FilenameHint) {
                if ($_.Name -like "*$FilenameHint*") { $matched = $true }
            }
            $matched
        } | Select-Object -First 1
        if ($hit) {
            $scope = if ($dir -eq $SysFontsDir) { "system-wide" } else { "per-user" }
            return @{ Found = $true; Scope = $scope; Path = $hit.FullName }
        }
    }
    return @{ Found = $false; Scope = ""; Path = "" }
}

# Filename-hint table for GlyphTypeface-fallback lookups. Keys are display
# names; values are the prefix used in TTF filenames downloaded from
# google/fonts.
$FilenameHints = @{
    "IBM Plex Sans"  = "IBMPlexSans"
    "IBM Plex Mono"  = "IBMPlexMono"
    "Hanken Grotesk" = "HankenGrotesk"
    "Barlow"         = "Barlow"
    "Host Grotesk"   = "HostGrotesk"
    "DM Sans"        = "DMSans"
    "Fira Code"      = "FiraCode"
}

# Derive the expected font families from the repo's fonts/ directory.
# We try to read the family name out of one TTF per family folder. WPF's
# GlyphTypeface throws on some variable fonts (e.g. DMSans) where optional
# name-table entries are missing - for those we fall back to a slug→name
# map keyed on the directory name.
$RepoFontsRoot = Join-Path (Split-Path $PSScriptRoot -Parent) "fonts"
$SlugToFamily = @{
    "ibm-plex-sans"  = "IBM Plex Sans"
    "ibm-plex-mono"  = "IBM Plex Mono"
    "hanken-grotesk" = "Hanken Grotesk"
    "barlow"         = "Barlow"
    "host-grotesk"   = "Host Grotesk"
    "dm-sans"        = "DM Sans"
    "fira-code"      = "Fira Code"
}
$ExpectedFamilies = @()
if (Test-Path $RepoFontsRoot) {
    Get-ChildItem $RepoFontsRoot -Directory -ErrorAction SilentlyContinue | Sort-Object Name | ForEach-Object {
        $dirName = $_.Name
        $sample = Get-ChildItem $_.FullName -Filter *.ttf -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $sample) { return }
        $fam = $null
        try {
            $uri = New-Object System.Uri($sample.FullName)
            $gt = New-Object System.Windows.Media.GlyphTypeface($uri)
            $fam = $gt.Win32FamilyNames["en-us"]
            if (-not $fam) { $fam = ($gt.Win32FamilyNames.Values | Select-Object -First 1) }
        } catch {
            $fam = $null
        }
        if (-not $fam) {
            # GlyphTypeface couldn't read this TTF; use the slug→name map.
            $fam = $SlugToFamily[$dirName]
        }
        if (-not $fam) {
            # Last resort: title-case the directory name.
            $fam = (Get-Culture).TextInfo.ToTitleCase($dirName.Replace("-", " "))
        }
        $ExpectedFamilies += $fam
    }
}
if ($ExpectedFamilies.Count -eq 0) {
    # Fallback if no fonts/ directory is found
    $ExpectedFamilies = @("IBM Plex Sans", "IBM Plex Mono")
}

foreach ($family in $ExpectedFamilies) {
    $hint = $FilenameHints[$family]
    if (-not $hint) { $hint = "" }
    $loc = Get-FontFamilyLocation -FamilyName $family -FilenameHint $hint
    if ($loc.Found) {
        Add-Check "$family installed" $true "$($loc.Scope) at $($loc.Path)"
    } else {
        Add-Check "$family installed" $false "Not in $SysFontsDir or $UserFontsDir"
    }
}

# Office artifacts
Add-Check "Office theme present" (Test-Path (Join-Path $ThemesDir "office-theme.thmx")) "$ThemesDir\office-theme.thmx"
Add-Check "Word template present" (Test-Path (Join-Path $TemplatesDir "deccan.dotx")) "$TemplatesDir\deccan.dotx"
Add-Check "PowerPoint template present" (Test-Path (Join-Path $TemplatesDir "deccan.potx")) "$TemplatesDir\deccan.potx"
Add-Check "Excel template present" (Test-Path (Join-Path $TemplatesDir "deccan.xltx")) "$TemplatesDir\deccan.xltx"

# Registry
foreach ($app in $Apps) {
    $regKey = "HKCU:\Software\Microsoft\Office\$OfficeVersion\$app\Options"
    $current = (Get-ItemProperty -Path $regKey -Name "PersonalTemplates" -ErrorAction SilentlyContinue).PersonalTemplates
    Add-Check "$app PersonalTemplates registry" ($current -eq $TemplatesDir) "Expected: $TemplatesDir; got: $(if ($current) { $current } else { '(not set)' })"
}

# Report
$pass = ($Checks | Where-Object { $_.Pass }).Count
$total = $Checks.Count
Write-Host "Deccan design system audit: $pass / $total checks passed" -ForegroundColor $(if ($pass -eq $total) { "Green" } else { "Yellow" })
Write-Host ""
foreach ($c in $Checks) {
    $marker = if ($c.Pass) { "[OK]" } else { "[FAIL]" }
    $color = if ($c.Pass) { "Green" } else { "Red" }
    Write-Host "  $marker $($c.Name)" -ForegroundColor $color
    if ($c.Detail) {
        Write-Host "       $($c.Detail)" -ForegroundColor DarkGray
    }
}

Pause-Before-Exit

if ($pass -eq $total) {
    exit 0
} else {
    exit 1
}
