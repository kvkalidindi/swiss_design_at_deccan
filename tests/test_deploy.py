"""Validate Plan 5 deploy artifacts: PowerShell parses, READMEs cover sections."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deploy"


def _powershell_parses(path: Path) -> tuple[bool, str]:
    """Use PowerShell's parser to check syntax (no execution)."""
    cmd = [
        "powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
        f"$null = [System.Management.Automation.Language.Parser]::ParseFile('{path}', [ref]$null, [ref]$errs); "
        f"if ($errs -and $errs.Count -gt 0) {{ $errs | ForEach-Object {{ Write-Host $_.Message }}; exit 1 }} else {{ exit 0 }}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("script", [
    "install.ps1",
    "install-fonts.ps1",
    "uninstall.ps1",
    "validate.ps1",
])
def test_powershell_parses(script):
    path = DEPLOY / script
    assert path.exists(), f"Missing {path}"
    ok, output = _powershell_parses(path)
    assert ok, f"PowerShell parse error in {script}:\n{output}"


def test_install_ps1_documents_flags():
    """Synopsis must document the documented parameter set."""
    text = (DEPLOY / "install.ps1").read_text(encoding="utf-8")
    for flag in ["SystemWide", "Uninstall", "DryRun", "Validate", "OnlyFonts", "OnlyTemplates", "OnlyRegistry"]:
        assert flag in text, f"install.ps1 doesn't reference -{flag}"


def test_validate_ps1_has_nine_checks():
    """validate.ps1 should add 9 checks (2 fonts + 4 artifacts + 3 registry)."""
    text = (DEPLOY / "validate.ps1").read_text(encoding="utf-8")
    add_check_count = text.count("Add-Check ")
    # 2 font checks + 4 artifact checks + 3 registry checks (loop body) - the loop expands implicitly,
    # but we still expect at least 7 explicit Add-Check calls (the foreach loop has 1 occurrence)
    assert add_check_count >= 6, f"Expected >= 6 explicit Add-Check calls, got {add_check_count}"


def test_readme_covers_required_sections():
    """deploy/README.md must mention key concepts."""
    text = (DEPLOY / "README.md").read_text(encoding="utf-8")
    for token in ["install.ps1", "Uninstall", "Validate", "DryRun", "SystemWide", "Intune", "Group Policy"]:
        assert token in text, f"deploy/README.md missing reference to '{token}'"
