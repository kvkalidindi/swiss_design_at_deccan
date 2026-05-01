#requires -Version 5.1
<#
.SYNOPSIS
    Audit the Deccan design system install state on this PC.

.DESCRIPTION
    Checks fonts, Office artifacts, and registry. Returns exit code 0 if all 9
    checks pass, non-zero otherwise. Used both interactively and by Intune
    detection scripts.

.EXAMPLE
    .\validate.ps1
    Run audit and print pass/fail report.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

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

# Check 1-2: fonts installed (look in user OR system fonts)
Add-Type -AssemblyName PresentationCore -ErrorAction SilentlyContinue
function Test-FontFamilyInstalled {
    param([string]$FamilyName)
    $userFonts = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
    $sysFonts = Join-Path $env:WINDIR "Fonts"
    foreach ($dir in @($userFonts, $sysFonts)) {
        if (-not (Test-Path $dir)) { continue }
        $found = Get-ChildItem $dir -Filter *.ttf -ErrorAction SilentlyContinue | Where-Object {
            try {
                $uri = New-Object System.Uri($_.FullName)
                $gt = New-Object System.Windows.Media.GlyphTypeface($uri)
                $family = $gt.Win32FamilyNames["en-us"]
                $family -eq $FamilyName
            } catch { $false }
        }
        if ($found) { return $true }
    }
    return $false
}

Add-Check "IBM Plex Sans installed" (Test-FontFamilyInstalled -FamilyName "IBM Plex Sans") "Required for theme + templates"
Add-Check "IBM Plex Mono installed" (Test-FontFamilyInstalled -FamilyName "IBM Plex Mono") "Used in code blocks"

# Check 3-6: Office artifacts present
Add-Check "Office theme present" (Test-Path (Join-Path $ThemesDir "office-theme.thmx")) "$ThemesDir\office-theme.thmx"
Add-Check "Word template present" (Test-Path (Join-Path $TemplatesDir "deccan.dotx")) "$TemplatesDir\deccan.dotx"
Add-Check "PowerPoint template present" (Test-Path (Join-Path $TemplatesDir "deccan.potx")) "$TemplatesDir\deccan.potx"
Add-Check "Excel template present" (Test-Path (Join-Path $TemplatesDir "deccan.xltx")) "$TemplatesDir\deccan.xltx"

# Check 7-9: registry
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
    if (-not $c.Pass) {
        Write-Host "       $($c.Detail)" -ForegroundColor DarkGray
    }
}

if ($pass -eq $total) {
    exit 0
} else {
    exit 1
}
