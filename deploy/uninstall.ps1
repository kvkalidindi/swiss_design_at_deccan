#requires -Version 5.1
<#
.SYNOPSIS
    Uninstall the Deccan design system from this PC.

.DESCRIPTION
    Wrapper around install.ps1 -Uninstall. Use this script if you prefer the
    explicit uninstall.ps1 entry point. All flags from install.ps1 are
    forwarded:
      -PerUser         match the scope of a previous -PerUser install
      -OnlyFonts       only remove fonts
      -OnlyTemplates   only remove Office artifacts
      -OnlyRegistry    only clear the PersonalTemplates registry keys
      -DryRun          preview without changes

    The pause-at-end behavior is handled by install.ps1; you'll see "Press
    Enter to close this window..." at the end.

.EXAMPLE
    .\uninstall.ps1
    Reverse a default (system-wide) install. Needs admin.

.EXAMPLE
    .\uninstall.ps1 -PerUser
    Reverse a per-user install. No admin needed.
#>
[CmdletBinding()]
param(
    [switch]$PerUser,
    [switch]$SystemWide,    # deprecated alias; kept for compatibility
    [switch]$DryRun,
    [switch]$OnlyFonts,
    [switch]$OnlyTemplates,
    [switch]$OnlyRegistry
)

$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) { $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }

$argsList = @("-Uninstall")
if ($PerUser) { $argsList += "-PerUser" }
if ($SystemWide) { $argsList += "-SystemWide" }
if ($DryRun) { $argsList += "-DryRun" }
if ($OnlyFonts) { $argsList += "-OnlyFonts" }
if ($OnlyTemplates) { $argsList += "-OnlyTemplates" }
if ($OnlyRegistry) { $argsList += "-OnlyRegistry" }

& (Join-Path $ScriptRoot "install.ps1") @argsList
