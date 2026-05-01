#requires -Version 5.1
<#
.SYNOPSIS
    Uninstall the Deccan design system from this PC.

.DESCRIPTION
    Wrapper that calls install.ps1 -Uninstall. Use this script if you prefer the
    explicit uninstall.ps1 entry point. All flags from install.ps1 are forwarded
    (use -SystemWide if you originally installed system-wide; -OnlyFonts /
    -OnlyTemplates / -OnlyRegistry for partial reverse).

.EXAMPLE
    .\uninstall.ps1
    Reverse a per-user install.

.EXAMPLE
    .\uninstall.ps1 -SystemWide
    Reverse a system-wide install (admin required).
#>
[CmdletBinding()]
param(
    [switch]$SystemWide,
    [switch]$DryRun,
    [switch]$OnlyFonts,
    [switch]$OnlyTemplates,
    [switch]$OnlyRegistry
)

$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) { $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }

$argsList = @("-Uninstall")
if ($SystemWide) { $argsList += "-SystemWide" }
if ($DryRun) { $argsList += "-DryRun" }
if ($OnlyFonts) { $argsList += "-OnlyFonts" }
if ($OnlyTemplates) { $argsList += "-OnlyTemplates" }
if ($OnlyRegistry) { $argsList += "-OnlyRegistry" }

& (Join-Path $ScriptRoot "install.ps1") @argsList
