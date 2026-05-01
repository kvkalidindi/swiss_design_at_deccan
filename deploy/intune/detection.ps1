#requires -Version 5.1
<#
.SYNOPSIS
    Intune detection script for the Deccan design system Win32 app.

.DESCRIPTION
    Intune calls this script to determine whether the app is installed.
    Conventions:
      - Exit code 0 + STDOUT output = "installed"
      - Exit code != 0 OR no output = "not installed"

    We re-use validate.ps1's pass/fail logic. If validate returns 0 (all 9
    checks pass), we emit a marker line to stdout and exit 0. Otherwise we
    emit nothing and exit 1, signaling Intune to (re)install.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) { $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }

# When packaged as IntuneWin, validate.ps1 is alongside this script. Try both layouts.
$validateCandidates = @(
    Join-Path $ScriptRoot "validate.ps1"                # flat layout
    Join-Path $ScriptRoot "..\validate.ps1"             # if detection.ps1 is in a subdir
)
$validateScript = $validateCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $validateScript) {
    # Detection failure: exit non-zero with no stdout
    exit 1
}

$null = & $validateScript -NoPause *>&1
if ($LASTEXITCODE -eq 0) {
    Write-Output "Deccan design system installed and validated."
    exit 0
} else {
    exit 1
}
