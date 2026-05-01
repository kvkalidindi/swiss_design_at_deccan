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

# Hashtable splatting (not array) so each switch binds by NAME. Array
# splatting would treat each "-X" string as a positional value and the
# CmdletBinding-decorated install.ps1 would reject it.
$splat = @{ Uninstall = $true }
if ($PerUser)       { $splat.PerUser       = $true }
if ($SystemWide)    { $splat.SystemWide    = $true }
if ($DryRun)        { $splat.DryRun        = $true }
if ($OnlyFonts)     { $splat.OnlyFonts     = $true }
if ($OnlyTemplates) { $splat.OnlyTemplates = $true }
if ($OnlyRegistry)  { $splat.OnlyRegistry  = $true }

& (Join-Path $ScriptRoot "install.ps1") @splat
